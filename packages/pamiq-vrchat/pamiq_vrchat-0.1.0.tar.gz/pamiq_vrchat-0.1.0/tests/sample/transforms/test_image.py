import numpy as np
import pytest
import torch

from sample.transforms.image import (
    ResizeAndCenterCrop,
    create_transform,
)
from tests.sample.helpers import parametrize_device


class TestResizeAndCenterCrop:
    @pytest.mark.parametrize(
        "input_shape,target_size,expected_shape",
        [
            ((3, 100, 200), (50, 50), (3, 50, 50)),
            ((3, 200, 100), (50, 50), (3, 50, 50)),
            ((1, 3, 400, 300), (100, 100), (1, 3, 100, 100)),
            # Aspect ratio < 1
            ((3, 200, 200), (50, 100), (3, 50, 100)),
            # Aspect ratio > 1
            ((3, 300, 300), (100, 50), (3, 100, 50)),
        ],
    )
    def test_output_shape(self, input_shape, target_size, expected_shape):
        transform = ResizeAndCenterCrop(target_size)
        input_tensor = torch.randn(input_shape)
        output = transform(input_tensor)
        assert output.shape == expected_shape

    @pytest.mark.parametrize(
        "input_shape,error_message",
        [
            ((10,), "Input tensor must have at least 3 dimensions, got 1"),
            ((3, 0, 100), r"Input image dimensions must be non-zero, got \(0, 100\)"),
            ((3, 100, 0), r"Input image dimensions must be non-zero, got \(100, 0\)"),
        ],
    )
    def test_invalid_input_errors(self, input_shape, error_message):
        transform = ResizeAndCenterCrop((50, 50))
        input_tensor = torch.randn(input_shape)
        with pytest.raises(ValueError, match=error_message):
            transform(input_tensor)

    def test_content_preservation(self):
        transform = ResizeAndCenterCrop((50, 50))
        input_tensor = torch.zeros(3, 100, 100)
        input_tensor[:, 40:60, 40:60] = 1.0

        output = transform(input_tensor)
        center_mean = output[:, 20:30, 20:30].mean()
        assert center_mean > 0.9


class TestCreateVRChatTransform:
    @pytest.mark.parametrize(
        "size,dtype",
        [
            ((224, 224), torch.float32),
            ((128, 128), torch.float32),
            ((512, 512), torch.float16),
        ],
    )
    @parametrize_device
    def test_full_pipeline(self, size, dtype, device):
        transform = create_transform(size, device, dtype)
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        output = transform(image)

        assert output.shape == (3, *size)
        assert output.dtype == dtype
        assert output.device == device
        assert output.mean().item() == pytest.approx(0.0, abs=1e-3)
        assert output.std().item() == pytest.approx(1.0, abs=1e-1)

    def test_preserves_content_structure(self):
        transform = create_transform((224, 224))
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        image[200:280, 300:340, :] = 255

        output = transform(image)
        center = output[:, 100:124, 100:124]
        edge = output[:, 0:24, 0:24]

        assert center.mean() != edge.mean()

    @pytest.mark.parametrize(
        "input_shape",
        [(100, 100, 3), (800, 600, 3), (1920, 1080, 3)],
    )
    def test_different_input_sizes(self, input_shape):
        transform = create_transform((256, 256))
        image = np.random.randint(0, 255, input_shape, dtype=np.uint8)

        output = transform(image)

        assert output.shape == (3, 256, 256)
        assert output.dtype == torch.float32
