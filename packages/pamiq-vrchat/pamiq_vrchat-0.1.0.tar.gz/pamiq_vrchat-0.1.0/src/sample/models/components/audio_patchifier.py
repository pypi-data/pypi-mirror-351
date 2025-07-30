# Ref:
# https://github.com/facebookresearch/fairseq/blob/main/fairseq/models/wav2vec/wav2vec2.py#L844
# https://github.com/facebookresearch/fairseq/blob/main/examples/data2vec/models/modalities/audio.py#L29

from typing import ClassVar, override

import torch
import torch.nn as nn


class ConvBlock(nn.Module):
    """Conv block to be used in AudioPatchifier."""

    @override
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int,
    ) -> None:
        """Initialize.

        Args:
            in_channels: Input channels.
            out_channels: Output channels.
            kernel_size: Kernel size of conv1d.
            stride: Kernel size of stride.
        """
        super().__init__()

        self.conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            bias=False,
        )
        nn.init.kaiming_normal_(self.conv.weight)
        self.layer_norm = nn.LayerNorm(out_channels, elementwise_affine=True)
        self.activation = nn.GELU()

    @override
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply conv1d, norm and activation.

        Args:
            x: Input features. Shape is [batch_size, in_channels, length].

        Returns:
            Output features. Shape is [batch_size, out_channels, floor((length - kernel_size)/stride) + 1].
        """
        x = self.conv(x)
        x = x.transpose(-2, -1)
        x = self.layer_norm(x)
        x = x.transpose(-2, -1)
        x = self.activation(x)
        return x


class AudioPatchifier(nn.Module):
    """Convert input audios into patch embeddings."""

    KERNEL_SIZES: ClassVar[tuple[int, ...]] = (10, 3, 3, 3, 3, 2, 2)
    STRIDES: ClassVar[tuple[int, ...]] = (5, 2, 2, 2, 2, 2, 2)

    @override
    def __init__(self, in_channels: int, embed_dim: int = 512) -> None:
        """

        Args:
            in_channels: Num of input audio channels.
            embed_dim: Num of embed dimensions per a patch.
        """
        super().__init__()

        # According to data2vec paper (https://arxiv.org/abs/2202.03555),
        # results in window_size=400[samples] and hop_size=320[samples] as total.

        self.conv_layers = nn.Sequential()
        for i, (k, s) in enumerate(zip(self.KERNEL_SIZES, self.STRIDES)):
            self.conv_layers.append(
                ConvBlock(
                    in_channels=in_channels if i == 0 else embed_dim,
                    out_channels=embed_dim,
                    kernel_size=k,
                    stride=s,
                )
            )

    @override
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Convert input audios into patches.

        Args:
            x: Input audios. Shape is [batch_size, n_channels, sample_size].

        Returns:
            Output patches. Shape is [batch_size, n_patches, embed_dim].
        """
        x = self.conv_layers(x)
        x = x.transpose(
            -1, -2
        )  # [batch_size, embed_dim, n_patches] -> [batch_size, n_patches, embed_dim]
        return x

    @classmethod
    def compute_num_patches(cls, sample_size: int) -> int:
        """Compute the number of patches that will be produced from input
        audio.

        Args:
            sample_size: Number of input audio samples.

        Returns:
            Number of patches that will be produced.

        Raises:
            ValueError: If sample_size is too small to produce any patches.
        """
        size = sample_size
        for i, (kernel_size, stride) in enumerate(zip(cls.KERNEL_SIZES, cls.STRIDES)):
            size = int((size - kernel_size) / stride + 1)
            if size <= 0:
                raise ValueError(
                    f"Input sample_size {sample_size} is too small. "
                    f"Failed at convolution layer {i} with kernel_size={kernel_size}, "
                    f"stride={stride}. Resulting size would be {size}."
                )
        return size
