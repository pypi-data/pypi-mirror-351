#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#
# noqa: F722

from beartype import beartype
from beartype.typing import Optional, Tuple, Union
from enum import Enum

import torch
import torch.nn as nn

from argmaxtools import tensor_typing as tt
from argmaxtools.utils import get_logger
from argmaxtools import _sdpa

logger = get_logger(__name__)


class AttentionType(Enum):
    SelfAttention = 1
    CausalSelfAttention = 2
    KVCachedSelfAttention = 3
    EncoderDecoderCrossAttention = 4
    KVCachedEncoderDecoderCrossAttention = 5


class AttentionHeadType(Enum):
    MultiHead = 1     # MHA: https://arxiv.org/abs/1706.03762
    GroupQuery = 2    # GQA: https://arxiv.org/abs/2305.13245
    MultiQuery = 3    # MQA: https://arxiv.org/pdf/1911.02150


DEFAULT_SDPA = _sdpa.Cat


@beartype
class Attention(nn.Module):
    """ Argmax reference attention implementation
    """
    def __init__(self,
                 embed_dim: int,
                 n_heads: int,
                 attention_type: AttentionType,
                 n_kv_heads: Optional[int] = None) -> None:
        """
        Args:
            embed_dim:          Number of embedding dimensions
            n_heads:            Number of attention heads
            attention_type:     Attention type
            n_kv_heads:         MHA if None, GQA if 1<n_kv_heads<n_heads
                                and MQA if n_kv_heads=1
        """
        super().__init__()

        # Configure dimensions for SDPA
        self.embed_dim = embed_dim
        self.n_heads = n_heads
        assert self.embed_dim % self.n_heads == 0

        # Select SDPA implementation, this is runtime configurable
        # (model interface or function does not change)
        self._sdpa_implementation = DEFAULT_SDPA(self.embed_dim, self.n_heads)

        # Assign attention_type (model interface and function might change)
        self.attention_type = attention_type

        # Configure head type
        self.n_kv_heads = n_kv_heads
        if n_kv_heads is None or n_kv_heads == n_heads:
            self.head_type = AttentionHeadType.MultiHead
        elif n_kv_heads == 1:
            self.head_type = AttentionHeadType.MultiQuery
        elif n_kv_heads > 1:
            assert n_kv_heads <= n_heads and n_heads % n_kv_heads == 0
            self.head_type = AttentionHeadType.GroupQuery
        else:
            raise ValueError(f"Invalid n_kv_heads ({n_kv_heads})")

        logger.debug(f"AttentionHeadType: {self.head_type}")

        # Initialize layers
        self.per_head_dim = self.embed_dim // self.n_heads
        self.kv_proj_embed_dim = self.per_head_dim * (n_kv_heads or n_heads)

        # Note: key bias is redundant due to softmax invariance
        self.k_proj = nn.Conv2d(embed_dim, self.kv_proj_embed_dim, 1, bias=False)
        self.q_proj = nn.Conv2d(embed_dim, embed_dim, 1)
        self.v_proj = nn.Conv2d(embed_dim, self.kv_proj_embed_dim, 1)
        self.o_proj = nn.Conv2d(embed_dim, embed_dim, 1)

        # Set private property for returning attention weights
        self._return_w = False

    @property
    def sdpa_implementation(self):
        return self._sdpa_implementation

    @sdpa_implementation.setter
    def sdpa_implementation(self, value):
        assert issubclass(value, _sdpa.SDPAImplementation)
        self._sdpa_implementation = value(self.embed_dim, self.n_heads)

    def _maybe_tile(self,
                    key: torch.Tensor,
                    value: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """ Tile key and value tensors before _sdpa() if head_type is GQA or MQA
        """
        if self.head_type != AttentionHeadType.MultiHead:
            repeats = self.embed_dim // self.kv_proj_embed_dim
            if key.shape[1] == self.kv_proj_embed_dim:
                key = key.repeat(1, repeats, 1, 1)
            if value.shape[1] == self.kv_proj_embed_dim:
                value = value.repeat(1, repeats, 1, 1)

        return key, value

    def forward(self,
                input_embeds: tt.InputEmbedsType,
                key_padding_mask: Optional[tt.AttentionMaskType] = None,
                key_cache: Optional[tt.KVCacheType] = None,
                value_cache: Optional[tt.KVCacheType] = None,
                kv_cache_update_mask: Optional[tt.AttentionMaskType] = None,
                encoder_output_embeds: Optional[tt.EncoderOutputEmbedsType] = None,
                qk_mask: Optional[tt.SDPAQKMaskType] = None,
                ) -> Union[
                    tt.SelfAttentionReturnType,
                    tt.EncoderDecoderAttentionReturnType,
                    tt.KVCachedSelfAttentionReturnType]:

        # Project input_embds to query, key and value
        query, current_key, current_value = self._qkv_proj(input_embeds,
                                                           encoder_output_embeds)

        # Configure the key and value tensors based on attention type
        key, value = self._finalize_kv(key_cache,
                                       value_cache,
                                       current_key,
                                       current_value,
                                       kv_cache_update_mask)

        # Compute scaled dot product attention
        attn = self._sdpa(query,
                          key,
                          value,
                          key_padding_mask,
                          qk_mask)

        if self._return_w:
            attn, attn_weights = attn

        # Final projection
        attn = self.o_proj(attn)

        outputs = (attn,)

        # If KV cached attention, return current key and value for cache updates
        if self.attention_type == AttentionType.KVCachedSelfAttention:
            outputs += (current_key, current_value)

        if self._return_w:
            outputs += (attn_weights,)

        return outputs

    def _qkv_proj(self,
                  input_embeds,
                  encoder_output_embeds):
        """ Compute qkv projections prescribed by currently active input configurations
        """
        if encoder_output_embeds is not None:
            if self.attention_type != AttentionType.EncoderDecoderCrossAttention:
                raise ValueError(
                    "`encoder_output_embeds` is only compatible with the "
                    "AttentionType.EncoderDecoderCrossAttention configuration")

            kv_proj_inputs = encoder_output_embeds
        else:
            kv_proj_inputs = input_embeds

        query = self.q_proj(input_embeds)

        if not self.attention_type == AttentionType.KVCachedEncoderDecoderCrossAttention:
            current_key = self.k_proj(kv_proj_inputs)
            current_value = self.v_proj(kv_proj_inputs)
        else:
            current_key = None
            current_value = None

        return query, current_key, current_value

    def _finalize_kv(self,
                     key_cache,
                     value_cache,
                     current_key,
                     current_value,
                     kv_cache_update_mask):
        """ Determine the key and value tensors based on attention type. If head_type is GQA or MQA,
        repeat key and value tensors to match the query tensor embedding dimensionality.
        """
        if self.attention_type == AttentionType.KVCachedSelfAttention:
            if self.sdpa_implementation.requires_prior_kv_cache_update:
                kv_cache_update_mask = kv_cache_update_mask[:, None, None, :]
                key_cache = key_cache * (1. - kv_cache_update_mask) + \
                    current_key * kv_cache_update_mask
                value_cache = value_cache * (1. - kv_cache_update_mask) + \
                    current_value * kv_cache_update_mask
                key = key_cache
                value = value_cache
            else:
                assert kv_cache_update_mask is None
                # If self._sdpa.requires_kv_cache_update is False, then
                # the caller should update the KV cache externally
                key = (key_cache, current_key)
                value = (value_cache, current_value)
                return key, value

        elif self.attention_type == AttentionType.KVCachedEncoderDecoderCrossAttention:
            assert key_cache is not None and value_cache is not None
            assert current_key is None and current_value is None
            key = key_cache
            value = value_cache

        elif self.attention_type in [AttentionType.SelfAttention,
                                     AttentionType.CausalSelfAttention,
                                     AttentionType.EncoderDecoderCrossAttention]:
            assert key_cache is None and value_cache is None
            key = current_key
            value = current_value
        else:
            raise ValueError(self.attention_type)

        # If not tiled upstream already
        key, value = self._maybe_tile(key, value)

        return key, value

    def _sdpa(self, query, key, value, key_padding_mask, qk_mask):
        """ Compute Scaled Dot Product Attention
        """
        return self._sdpa_implementation.sdpa(
            query, key, value, key_padding_mask,
            causal=self.attention_type == AttentionType.CausalSelfAttention,
            return_w=self._return_w,
            qk_mask=qk_mask,
        )


class SharedSplitKVCachedSelfAttention(Attention):
    """ Argmax reference attention implementation for large
    batch_size `input_embeds` and batch_size=1 `{key,value}_cache`
    """
    def __init__(self,
                 embed_dim: int,
                 n_heads: int,
                 attention_type: Optional[AttentionType] = AttentionType.KVCachedSelfAttention,
                 n_kv_heads: Optional[int] = None) -> None:
        if attention_type != AttentionType.KVCachedSelfAttention:
            raise ValueError(
                f"{self.__class__} is only compatible with "
                f"{AttentionType.KVCachedSelfAttention}")
        super().__init__(embed_dim, n_heads, attention_type, n_kv_heads)
        self._sdpa_implementation = _sdpa.SharedSplitKVCached(self.embed_dim, self.n_heads)

    @property
    def sdpa_implementation(self):
        return self._sdpa_implementation

    @sdpa_implementation.setter
    def sdpa_implementation(self, value):
        logger.warning(
            "sdpa_implementation can not be set for SharedSplitKVCachedSelfAttention")

    def forward(self,
                input_embeds: tt.InputEmbedsType,
                key_padding_mask: Optional[tt.AttentionMaskType] = None,
                key_cache: Optional[tt.KVCacheType] = None,
                value_cache: Optional[tt.KVCacheType] = None,
                kv_cache_update_mask: Optional[tt.AttentionMaskType] = None,
                # encoder_output_embeds: Optional[tt.EncoderOutputEmbedsType] = None,
                qk_mask: Optional[tt.SDPAQKMaskType] = None,
                ) -> tt.KVCachedSelfAttentionReturnType:
        """ TODO: Document I/O
        """
        return super().forward(
            input_embeds,
            key_padding_mask,
            key_cache,
            value_cache,
            None,
            None,
            qk_mask)


class StatefulKVCachedAttention(Attention):
    def __init__(self, embed_dim, n_heads, max_kv_seq_len, n_kv_heads=None):
        super().__init__(embed_dim, n_heads, AttentionType.KVCachedSelfAttention, n_kv_heads)
        cache_shape = (1, embed_dim, 1, max_kv_seq_len)
        self.register_buffer("key_cache", torch.zeros(*cache_shape))
        self.register_buffer("value_cache", torch.zeros(*cache_shape))

    @classmethod
    def from_attention(cls, attention, max_kv_seq_len):
        return cls(attention.embed_dim, attention.n_heads, max_kv_seq_len, attention.n_kv_heads)

    def forward(self,
                input_embeds: tt.InputEmbedsType,
                key_padding_mask: Optional[tt.AttentionMaskType] = None,
                kv_cache_update_mask: Optional[tt.AttentionMaskType] = None,
                encoder_output_embeds: Optional[tt.EncoderOutputEmbedsType] = None,
                qk_mask: Optional[tt.SDPAQKMaskType] = None,
                ) -> tt.SelfAttentionReturnType:
        # Provide internal states as KV cache and do not output the unnecessary cache updates
        return super().forward(
            input_embeds,
            key_padding_mask,
            self.key_cache,
            self.value_cache,
            kv_cache_update_mask,
            encoder_output_embeds,
            qk_mask)


class StatefulSharedSplitKVCachedSelfAttention(StatefulKVCachedAttention):
    """ Argmax reference attention implementation for large
    batch_size `input_embeds` and batch_size=1 `{key,value}_cache`
    """
    def _finalize_kv(self,
                     key_cache,
                     value_cache,
                     current_key,
                     current_value,
                     kv_cache_update_mask):
        """ Determine the key and value tensors based on attention type. If head_type is GQA or MQA,
        repeat key and value tensors to match the query tensor embedding dimensionality.
        """
        if self.attention_type != AttentionType.KVCachedSelfAttention:
            raise ValueError(
                f"{self.__class__} is only compatible with "
                f"{AttentionType.KVCachedSelfAttention}")

        key_cache, value_cache = self._maybe_tile(key_cache, value_cache)
        current_key, current_value = self._maybe_tile(current_key, current_value)

        # Keep unmerged
        key = (key_cache, current_key)
        value = (value_cache, current_value)

        return key, value

    def _sdpa(self, query, key, value, key_padding_mask, qk_mask):
        """ Compute Scaled Dot Product Attention
        """
        if self._return_w:
            raise NotImplementedError("TODO")

        return _sdpa.SharedSplitKVCached(self.embed_dim, self.n_heads).sdpa(
            query, key, value, key_padding_mask,
            causal=self.attention_type == AttentionType.CausalSelfAttention,
            return_w=self._return_w,
            qk_mask=qk_mask,
        )


class StatefulKVCachedEncoderDecoderCrossAttention(Attention):
    def __init__(self, embed_dim, n_heads, max_kv_seq_len, n_kv_heads=None):
        super().__init__(
            embed_dim, n_heads, AttentionType.KVCachedEncoderDecoderCrossAttention, n_kv_heads)
        cache_shape = (1, embed_dim, 1, max_kv_seq_len)
        self.register_buffer("key_cache", torch.zeros(*cache_shape))
        self.register_buffer("value_cache", torch.zeros(*cache_shape))

        # Delete projections that are not going to be used in the decoder
        # (Encoder should have them instead)
        delattr(self, "k_proj")
        delattr(self, "v_proj")

    @classmethod
    def from_attention(cls, attention, max_kv_seq_len):
        return cls(attention.embed_dim, attention.n_heads, max_kv_seq_len, attention.n_kv_heads)

    def forward(self,
                input_embeds: tt.InputEmbedsType,
                key_padding_mask: Optional[tt.AttentionMaskType] = None,
                kv_cache_update_mask: Optional[tt.AttentionMaskType] = None,
                encoder_output_embeds: Optional[tt.EncoderOutputEmbedsType] = None,
                qk_mask: Optional[tt.SDPAQKMaskType] = None,
                ) -> tt.SelfAttentionReturnType:
        # Provide internal states as KV cache and do not output the unnecessary cache updates
        return super().forward(
            input_embeds,
            key_padding_mask,
            self.key_cache,
            self.value_cache,
            kv_cache_update_mask,
            encoder_output_embeds,
            qk_mask)


class FFN(nn.Module):
    def __init__(self, embed_dim, expansion_factor, activation_fn):
        super().__init__()
        self.fc1 = nn.Conv2d(embed_dim, embed_dim * expansion_factor, 1)
        self.act_fn = activation_fn
        self.fc2 = nn.Conv2d(embed_dim * expansion_factor, embed_dim, 1)

    def forward(self, x):
        return self.fc2(self.act_fn(self.fc1(x)))


# Reference:
# https://github.com/apple/ml-ane-transformers/blob/main/ane_transformers/reference/layer_norm.py
class LayerNorm(nn.Module):
    def __init__(self,
                 num_channels,
                 clip_mag=None,
                 eps=1e-5,
                 elementwise_affine=True):

        super().__init__()
        self.num_channels = num_channels
        self.eps = eps
        self.clip_mag = clip_mag
        self.elementwise_affine = elementwise_affine

        if self.elementwise_affine:
            self.weight = nn.Parameter(torch.Tensor(num_channels))
            self.bias = nn.Parameter(torch.Tensor(num_channels))

            self.weight.data = torch.ones_like(self.weight.data)
            self.bias.data = torch.zeros_like(self.bias.data)

    def forward(self, inputs):
        input_rank = len(inputs.size())
        if input_rank != 4:
            raise ValueError(f"Incorrect input rank (Expected 4, got {input_rank})")

        if self.clip_mag is not None:
            inputs.clamp_(-self.clip_mag, self.clip_mag)

        channels_mean = inputs.mean(dim=1, keepdims=True)

        zero_mean = inputs - channels_mean
        zero_mean_sq = zero_mean * zero_mean

        denom = (zero_mean_sq.mean(dim=1, keepdims=True) + self.eps).rsqrt()

        out = zero_mean * denom

        if self.elementwise_affine:
            w = self.weight.view(1, self.num_channels, 1, 1)
            b = self.bias.view(1, self.num_channels, 1, 1)
            out = w * out + b

        return out


class RMSNorm(nn.Module):
    def __init__(self,
                 num_channels,
                 eps=1e-6,
                 clip_mag=None,):

        super().__init__()
        self.num_channels = num_channels
        self.eps = eps
        self.clip_mag = clip_mag
        self.weight = nn.Parameter(torch.Tensor(num_channels))
        self.weight.data = torch.ones_like(self.weight.data)

    def forward(self, inputs):
        if self.clip_mag is not None:
            inputs.clamp_(-self.clip_mag, self.clip_mag)

        input_rank = len(inputs.size())
        if input_rank != 4:
            raise ValueError(f"Incorrect input rank (Expected 4, got {input_rank})")

        inputs_sq = inputs * inputs
        variance = inputs_sq.mean(dim=1, keepdim=True)
        hidden_states = inputs * torch.rsqrt(variance + self.eps)

        w = self.weight.view(1, self.num_channels, 1, 1)
        out = w * hidden_states

        return out
