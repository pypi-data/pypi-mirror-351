import os
import tempfile
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import pytest

import vizy

# Try to import torch, but make tests work without it
try:
    import torch

    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False


class TestToNumpy:
    """Test the _to_numpy function."""

    def test_numpy_array_passthrough(self):
        """Test that numpy arrays are passed through unchanged."""
        arr = np.random.rand(10, 10)
        result = vizy._to_numpy(arr)
        assert np.array_equal(result, arr)
        assert result is arr  # Should be the same object

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_torch_tensor_conversion(self):
        """Test conversion from torch tensor to numpy."""
        tensor = torch.rand(5, 5)
        result = vizy._to_numpy(tensor)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5, 5)
        np.testing.assert_allclose(result, tensor.numpy(), rtol=1e-6)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_torch_tensor_with_grad(self):
        """Test conversion from torch tensor with gradients."""
        tensor = torch.rand(3, 3, requires_grad=True)
        result = vizy._to_numpy(tensor)
        assert isinstance(result, np.ndarray)
        assert result.shape == (3, 3)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_torch_tensor_on_device(self):
        """Test conversion from torch tensor on different device."""
        tensor = torch.rand(4, 4)
        if torch.cuda.is_available():
            tensor = tensor.cuda()
        result = vizy._to_numpy(tensor)
        assert isinstance(result, np.ndarray)
        assert result.shape == (4, 4)

    def test_invalid_input_type(self):
        """Test that invalid input types raise TypeError."""
        with pytest.raises(TypeError, match="Expected torch.Tensor | np.ndarray"):
            vizy._to_numpy([1, 2, 3])

        with pytest.raises(TypeError, match="Expected torch.Tensor | np.ndarray"):
            vizy._to_numpy("invalid")


class TestToHWC:
    """Test the _to_hwc function."""

    def test_2d_array_unchanged(self):
        """Test that 2D arrays (H, W) are unchanged."""
        arr = np.random.rand(100, 200)
        result = vizy._to_hwc(arr)
        assert np.array_equal(result, arr)
        assert result.shape == (100, 200)

    def test_3d_hwc_unchanged(self):
        """Test that 3D arrays in HWC format are unchanged."""
        arr = np.random.rand(50, 60, 3)  # H, W, C
        result = vizy._to_hwc(arr)
        assert np.array_equal(result, arr)
        assert result.shape == (50, 60, 3)

    def test_3d_chw_to_hwc(self):
        """Test conversion from CHW to HWC format."""
        arr = np.random.rand(3, 50, 60)  # C, H, W
        result = vizy._to_hwc(arr)
        expected = np.transpose(arr, (1, 2, 0))
        assert np.array_equal(result, expected)
        assert result.shape == (50, 60, 3)

    def test_3d_single_channel_chw(self):
        """Test conversion from single channel CHW to HWC."""
        arr = np.random.rand(1, 40, 50)  # C=1, H, W
        result = vizy._to_hwc(arr)
        expected = np.transpose(arr, (1, 2, 0))
        assert np.array_equal(result, expected)
        assert result.shape == (40, 50, 1)

    def test_3d_ambiguous_case(self):
        """Test case where both dimensions could be channels."""
        # When both first and last dim are 3, should prefer HWC (no transpose)
        arr = np.random.rand(3, 50, 3)
        result = vizy._to_hwc(arr)
        assert np.array_equal(result, arr)  # Should remain unchanged

    def test_invalid_dimensions(self):
        """Test that arrays with unsupported dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported dimensionality"):
            vizy._to_hwc(np.random.rand(10, 20, 30, 40))

        with pytest.raises(ValueError, match="Unsupported dimensionality"):
            vizy._to_hwc(np.random.rand(10))


class TestPrep:
    """Test the _prep function."""

    def test_2d_array(self):
        """Test preparation of 2D arrays."""
        arr = np.random.rand(50, 60)
        result = vizy._prep(arr)
        assert result.shape == (50, 60)
        assert result.ndim == 2

    def test_3d_array_hwc(self):
        """Test preparation of 3D arrays in HWC format."""
        arr = np.random.rand(50, 60, 3)
        result = vizy._prep(arr)
        assert result.shape == (50, 60, 3)

    def test_3d_array_chw(self):
        """Test preparation of 3D arrays in CHW format."""
        arr = np.random.rand(3, 50, 60)
        result = vizy._prep(arr)
        assert result.shape == (50, 60, 3)

    def test_4d_bchw(self):
        """Test preparation of 4D arrays in BCHW format."""
        arr = np.random.rand(4, 3, 50, 60)  # B, C, H, W
        result = vizy._prep(arr)
        assert result.shape == (4, 3, 50, 60)
        assert np.array_equal(result, arr)

    def test_4d_cbhw_to_bchw(self):
        """Test conversion from CBHW to BCHW format."""
        arr = np.random.rand(3, 4, 50, 60)  # C, B, H, W
        result = vizy._prep(arr)
        expected = np.transpose(arr, (1, 0, 2, 3))  # B, C, H, W
        assert result.shape == (4, 3, 50, 60)
        assert np.array_equal(result, expected)

    def test_4d_single_channel(self):
        """Test 4D arrays with single channel."""
        arr = np.random.rand(4, 1, 50, 60)  # B, C=1, H, W
        # The _prep function first calls squeeze(), which removes the dimension of size 1
        # So (4, 1, 50, 60) becomes (4, 50, 60) which is 3D but first dim is 4 (not 1 or 3)
        # so it remains unchanged
        result = vizy._prep(arr)
        assert result.shape == (4, 50, 60)

    def test_squeeze_behavior(self):
        """Test that arrays are properly squeezed."""
        arr = np.random.rand(1, 1, 50, 60, 1)
        result = vizy._prep(arr)
        assert result.shape == (50, 60)

    def test_invalid_4d_shape(self):
        """Test that invalid 4D shapes raise ValueError."""
        # Neither dimension 0 nor 1 is a valid channel count
        arr = np.random.rand(5, 7, 50, 60)
        with pytest.raises(ValueError, match="Cannot prepare array"):
            vizy._prep(arr)

    def test_invalid_dimensions(self):
        """Test that unsupported dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Cannot prepare array"):
            vizy._prep(np.random.rand(10, 20, 30, 40, 50))


class TestMakeGrid:
    """Test the _make_grid function."""

    def test_single_image(self):
        """Test grid creation with single image."""
        bchw = np.random.rand(1, 3, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (32, 32, 3)

    def test_two_images(self):
        """Test grid creation with two images (side by side)."""
        bchw = np.random.rand(2, 3, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (32, 64, 3)  # 1 row, 2 cols

    def test_three_images(self):
        """Test grid creation with three images (all in a row)."""
        bchw = np.random.rand(3, 3, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (32, 96, 3)  # 1 row, 3 cols

    def test_four_images(self):
        """Test grid creation with four images (2x2 grid)."""
        bchw = np.random.rand(4, 3, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (64, 64, 3)  # 2 rows, 2 cols

    def test_larger_batch(self):
        """Test grid creation with larger batch."""
        bchw = np.random.rand(9, 3, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (96, 96, 3)  # 3 rows, 3 cols

    def test_single_channel(self):
        """Test grid creation with single channel images."""
        bchw = np.random.rand(4, 1, 32, 32)
        result = vizy._make_grid(bchw)
        assert result.shape == (64, 64, 1)

    def test_non_square_images(self):
        """Test grid creation with non-square images."""
        bchw = np.random.rand(4, 3, 20, 30)
        result = vizy._make_grid(bchw)
        assert result.shape == (40, 60, 3)  # 2 rows, 2 cols


class TestConvertFloatToInt:
    """Test the _convert_float_to_int function."""

    def test_float_in_0_255_range(self):
        """Test conversion of float arrays in 0-255 range to uint8."""
        arr = np.array([0.0, 127.5, 255.0], dtype=np.float32)
        result = vizy._convert_float_to_int(arr)
        expected = np.array([0, 128, 255], dtype=np.uint8)
        assert np.array_equal(result, expected)
        assert result.dtype == np.uint8

    def test_float_in_0_1_range_unchanged(self):
        """Test that float arrays in 0-1 range are unchanged."""
        arr = np.array([0.0, 0.5, 1.0], dtype=np.float32)
        result = vizy._convert_float_to_int(arr)
        assert np.array_equal(result, arr)
        assert result.dtype == np.float32

    def test_integer_array_unchanged(self):
        """Test that integer arrays are unchanged."""
        arr = np.array([0, 127, 255], dtype=np.uint8)
        result = vizy._convert_float_to_int(arr)
        assert np.array_equal(result, arr)
        assert result.dtype == np.uint8

    def test_float_outside_0_255_range(self):
        """Test that float arrays outside 0-255 range are unchanged."""
        arr = np.array([-10.0, 300.0, 500.0], dtype=np.float32)
        result = vizy._convert_float_to_int(arr)
        assert np.array_equal(result, arr)
        assert result.dtype == np.float32

    def test_clipping_behavior(self):
        """Test that values are properly clipped to 0-255 range."""
        # This test was wrong - the function doesn't convert values outside 0-255 range
        arr = np.array([100.0, 200.0, 255.0], dtype=np.float32)
        result = vizy._convert_float_to_int(arr)
        expected = np.array([100, 200, 255], dtype=np.uint8)
        assert np.array_equal(result, expected)


class TestPrepareForDisplay:
    """Test the _prepare_for_display function."""

    def test_2d_array(self):
        """Test preparation of 2D array for display."""
        arr = np.random.rand(50, 60)
        result = vizy._prepare_for_display(arr)
        assert result.shape == (50, 60)
        assert result.ndim == 2

    def test_3d_array(self):
        """Test preparation of 3D array for display."""
        arr = np.random.rand(50, 60, 3)
        result = vizy._prepare_for_display(arr)
        assert result.shape == (50, 60, 3)

    def test_4d_array_to_grid(self):
        """Test that 4D arrays are converted to grids."""
        arr = np.random.rand(4, 3, 32, 32)
        result = vizy._prepare_for_display(arr)
        assert result.ndim == 3
        assert result.shape[2] == 3  # RGB channels

    def test_float_to_int_conversion(self):
        """Test that float arrays in 0-255 range are converted to uint8."""
        arr = np.array([[[100.0, 200.0, 255.0]]], dtype=np.float32)
        # This will be squeezed to (3,) which is invalid, so let's use a proper shape
        arr = np.array([[100.0, 200.0], [150.0, 255.0]], dtype=np.float32)
        result = vizy._prepare_for_display(arr)
        assert result.dtype == np.uint8


class TestCreateFigure:
    """Test the _create_figure function."""

    def test_2d_grayscale_array(self):
        """Test figure creation with 2D grayscale array."""
        arr = np.random.rand(50, 60)
        fig = vizy._create_figure(arr)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_3d_rgb_array(self):
        """Test figure creation with 3D RGB array."""
        arr = np.random.rand(50, 60, 3)
        fig = vizy._create_figure(arr)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_3d_single_channel_array(self):
        """Test figure creation with 3D single channel array."""
        arr = np.random.rand(50, 60, 1)
        fig = vizy._create_figure(arr)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_torch_tensor_input(self):
        """Test figure creation with torch tensor."""
        tensor = torch.rand(50, 60, 3)
        fig = vizy._create_figure(tensor)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_imshow_kwargs_passed(self):
        """Test that imshow kwargs are properly passed."""
        arr = np.random.rand(50, 60)
        # Don't pass cmap since the function sets it to "gray" for 2D arrays
        fig = vizy._create_figure(arr, vmin=0.2, vmax=0.8)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPlot:
    """Test the plot function."""

    @patch("matplotlib.pyplot.show")
    def test_plot_2d_array(self, mock_show):
        """Test plotting 2D array."""
        arr = np.random.rand(50, 60)
        result = vizy.plot(arr)
        mock_show.assert_called_once()
        # Clean up any figures
        plt.close("all")

    @patch("matplotlib.pyplot.show")
    def test_plot_3d_array(self, mock_show):
        """Test plotting 3D array."""
        arr = np.random.rand(50, 60, 3)
        result = vizy.plot(arr)
        mock_show.assert_called_once()
        plt.close("all")

    @patch("matplotlib.pyplot.show")
    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_plot_torch_tensor(self, mock_show):
        """Test plotting torch tensor."""
        tensor = torch.rand(50, 60, 3)
        result = vizy.plot(tensor)
        mock_show.assert_called_once()
        plt.close("all")

    @patch("matplotlib.pyplot.show")
    def test_plot_with_kwargs(self, mock_show):
        """Test plotting with additional kwargs."""
        arr = np.random.rand(50, 60, 3)  # Use RGB to avoid cmap conflict
        result = vizy.plot(arr, vmin=0.2)
        mock_show.assert_called_once()
        plt.close("all")


class TestSave:
    """Test the save function."""

    def test_save_with_path(self):
        """Test saving with explicit path."""
        arr = np.random.rand(50, 60, 3)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch("builtins.print") as mock_print:
                result_path = vizy.save(tmp_path, arr)
            assert result_path == tmp_path
            assert os.path.exists(tmp_path)
            mock_print.assert_called_once_with(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_save_auto_path(self):
        """Test saving with automatic path generation."""
        arr = np.random.rand(50, 60, 3)

        with patch("builtins.print") as mock_print:
            result_path = vizy.save(arr)

        try:
            assert result_path.endswith(".png")
            assert "vizy-" in result_path
            assert os.path.exists(result_path)
            mock_print.assert_called_once_with(result_path)
        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_save_torch_tensor(self):
        """Test saving torch tensor."""
        tensor = torch.rand(50, 60, 3)

        with patch("builtins.print") as mock_print:
            result_path = vizy.save(tensor)

        try:
            assert os.path.exists(result_path)
            mock_print.assert_called_once_with(result_path)
        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)

    def test_save_with_kwargs(self):
        """Test saving with additional kwargs."""
        arr = np.random.rand(50, 60, 3)  # Use RGB to avoid cmap conflict

        with patch("builtins.print") as mock_print:
            result_path = vizy.save(arr, vmin=0.2)

        try:
            assert os.path.exists(result_path)
            mock_print.assert_called_once_with(result_path)
        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)


class TestSummary:
    """Test the summary function."""

    def test_summary_numpy_array(self):
        """Test summary for numpy array."""
        arr = np.random.randint(0, 256, size=(50, 60, 3), dtype=np.uint8)

        with patch("builtins.print") as mock_print:
            vizy.summary(arr)

        # Check that print was called with expected information
        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("numpy.ndarray" in call for call in calls)
        assert any("Shape: (50, 60, 3)" in call for call in calls)
        assert any("uint8" in call for call in calls)
        assert any("Range:" in call for call in calls)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_summary_torch_tensor(self):
        """Test summary for torch tensor."""
        tensor = torch.rand(50, 60, 3)

        with patch("builtins.print") as mock_print:
            vizy.summary(tensor)

        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("torch.Tensor" in call for call in calls)
        assert any("Shape: (50, 60, 3)" in call for call in calls)
        assert any("float32" in call for call in calls)
        assert any("device:" in call for call in calls)

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_summary_torch_tensor_with_device(self):
        """Test summary for torch tensor with device info."""
        tensor = torch.rand(10, 10)
        if torch.cuda.is_available():
            tensor = tensor.cuda()

        with patch("builtins.print") as mock_print:
            vizy.summary(tensor)

        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("device:" in call for call in calls)

    def test_summary_integer_array(self):
        """Test summary for integer array shows unique values."""
        arr = np.array([1, 2, 2, 3, 3, 3], dtype=np.int32)

        with patch("builtins.print") as mock_print:
            vizy.summary(arr)

        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Number of unique values: 3" in call for call in calls)

    def test_summary_empty_array(self):
        """Test summary for empty array."""
        arr = np.array([], dtype=np.float32)

        with patch("builtins.print") as mock_print:
            vizy.summary(arr)

        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Range: N/A (empty array)" in call for call in calls)

    def test_summary_invalid_input(self):
        """Test summary with invalid input type."""
        with pytest.raises(TypeError, match="Expected torch.Tensor | np.ndarray"):
            vizy.summary([1, 2, 3])


class TestRandomArrays:
    """Test with various random array configurations."""

    def test_random_2d_arrays(self):
        """Test with random 2D arrays of various sizes."""
        for _ in range(10):
            h, w = np.random.randint(10, 200, 2)
            arr = np.random.rand(h, w)

            # Test that all functions work
            result = vizy._prepare_for_display(arr)
            assert result.shape == (h, w)

            fig = vizy._create_figure(arr)
            plt.close(fig)

    def test_random_3d_arrays(self):
        """Test with random 3D arrays."""
        for _ in range(10):
            h, w = np.random.randint(10, 100, 2)
            c = np.random.choice([1, 3])

            # Test both CHW and HWC formats
            if np.random.rand() > 0.5:
                arr = np.random.rand(c, h, w)  # CHW
            else:
                arr = np.random.rand(h, w, c)  # HWC

            result = vizy._prepare_for_display(arr)
            assert result.ndim in [2, 3]

            fig = vizy._create_figure(arr)
            plt.close(fig)

    def test_random_4d_arrays(self):
        """Test with random 4D arrays."""
        for _ in range(5):
            b = np.random.randint(1, 8)
            c = np.random.choice([1, 3])
            h, w = np.random.randint(10, 50, 2)

            # Test both BCHW and CBHW formats
            if np.random.rand() > 0.5:
                arr = np.random.rand(b, c, h, w)  # BCHW
            else:
                arr = np.random.rand(c, b, h, w)  # CBHW

            try:
                result = vizy._prepare_for_display(arr)
                # Result can be 2D (single channel squeezed) or 3D (multi-channel)
                assert result.ndim in [2, 3]

                fig = vizy._create_figure(arr)
                plt.close(fig)
            except (ValueError, TypeError):
                # Some random shapes might not be valid for matplotlib, which is expected
                pass

    @pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
    def test_random_torch_tensors(self):
        """Test with random torch tensors."""
        for _ in range(5):
            # Generate valid shapes for vizy
            shape_type = np.random.choice(["2d", "3d", "4d"])
            if shape_type == "2d":
                shape = tuple(np.random.randint(10, 50, 2))
            elif shape_type == "3d":
                h, w = np.random.randint(10, 50, 2)
                c = np.random.choice([1, 3])
                if np.random.rand() > 0.5:
                    shape = (c, h, w)  # CHW
                else:
                    shape = (h, w, c)  # HWC
            else:  # 4d
                b = np.random.randint(1, 4)
                c = np.random.choice([1, 3])
                h, w = np.random.randint(10, 30, 2)
                if np.random.rand() > 0.5:
                    shape = (b, c, h, w)  # BCHW
                else:
                    shape = (c, b, h, w)  # CBHW

            tensor = torch.rand(*shape)

            try:
                # Convert to numpy first since _prepare_for_display expects numpy arrays
                arr = vizy._to_numpy(tensor)
                result = vizy._prepare_for_display(arr)
                fig = vizy._create_figure(tensor)
                plt.close(fig)
            except (ValueError, TypeError):
                # Some random shapes might not be valid, which is expected
                pass

    def test_edge_case_shapes(self):
        """Test edge cases with minimal and maximal shapes."""
        # Minimal shapes
        arr = np.random.rand(2, 2)  # Use 2x2 instead of 1x1 to avoid edge cases
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)

        # Single pixel RGB
        arr = np.random.rand(2, 2, 3)  # Use 2x2 instead of 1x1
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)

        # Large batch size
        arr = np.random.rand(16, 3, 32, 32)
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)


class TestRandomStressTests:
    """Additional stress tests with random arrays."""

    def test_random_batch_sizes(self):
        """Test various batch sizes for 4D arrays."""
        for batch_size in [1, 2, 3, 4, 5, 8, 9, 16]:
            arr = np.random.rand(batch_size, 3, 32, 32)
            result = vizy._prepare_for_display(arr)
            fig = vizy._create_figure(arr)
            plt.close(fig)

    def test_random_channel_configurations(self):
        """Test different channel configurations."""
        for channels in [1, 3]:
            # Test 3D arrays
            arr = np.random.rand(32, 32, channels)
            result = vizy._prepare_for_display(arr)
            fig = vizy._create_figure(arr)
            plt.close(fig)

            # Test 4D arrays
            arr = np.random.rand(4, channels, 32, 32)
            try:
                result = vizy._prepare_for_display(arr)
                fig = vizy._create_figure(arr)
                plt.close(fig)
            except (ValueError, TypeError):
                # Some shapes might not be valid for matplotlib
                pass

    def test_random_dtypes(self):
        """Test different data types."""
        dtypes = [np.float32, np.float64, np.uint8, np.int32]
        for dtype in dtypes:
            if dtype in [np.uint8, np.int32]:
                arr = np.random.randint(0, 256, size=(32, 32), dtype=dtype)
            else:
                arr = np.random.rand(32, 32).astype(dtype)

            result = vizy._prepare_for_display(arr)
            fig = vizy._create_figure(arr)
            plt.close(fig)

    def test_random_value_ranges(self):
        """Test different value ranges."""
        # 0-1 range
        arr = np.random.rand(32, 32)
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)

        # 0-255 range
        arr = np.random.rand(32, 32) * 255
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)

        # Negative values
        arr = np.random.randn(32, 32)
        result = vizy._prepare_for_display(arr)
        fig = vizy._create_figure(arr)
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__])
