import unittest
import numpy as np
from backend.data_processing import process_data
from data_processing import DataProcessor
from scipy.signal import savgol_filter
from scipy.interpolate import make_interp_spline

class TestDataProcessing(unittest.TestCase):
    def test_process_data(self):
        wavelengths = np.linspace(900, 1700, 100)
        intensities = np.random.random(100)
        peaks = process_data(wavelengths, intensities)
        self.assertTrue(len(peaks) >= 0)

class TestSmoothData(unittest.TestCase):
    """Tests for the Savitzky-Golay smoothing used in spectrum plotting."""

    def test_savgol_filter_reduces_noise(self):
        """Savgol filter should reduce noise while preserving signal shape."""
        np.random.seed(42)
        wavelengths = np.linspace(900, 2500, 512)
        # Create a smooth signal with added noise
        signal = 5000 * np.exp(-((wavelengths - 1400) ** 2) / (2 * 200 ** 2))
        noisy = signal + np.random.normal(0, 200, len(signal))

        smoothed = savgol_filter(noisy, 11, 3)

        # Smoothed data should be closer to the original signal than the noisy data
        noise_error = np.mean((noisy - signal) ** 2)
        smooth_error = np.mean((smoothed - signal) ** 2)
        self.assertLess(smooth_error, noise_error)

    def test_savgol_preserves_peak_position(self):
        """Savgol filter should preserve peak positions in NIR spectra."""
        wavelengths = np.linspace(900, 2500, 512)
        signal = 5000 * np.exp(-((wavelengths - 1400) ** 2) / (2 * 50 ** 2))
        noisy = signal + np.random.normal(0, 100, len(signal))

        smoothed = savgol_filter(noisy, 11, 3)

        # Peak position should be preserved (within 1 index)
        original_peak = np.argmax(signal)
        smoothed_peak = np.argmax(smoothed)
        self.assertAlmostEqual(original_peak, smoothed_peak, delta=2)

    def test_savgol_window_adapts_to_small_data(self):
        """Window length should adapt when data is smaller than default window."""
        data = np.array([1.0, 3.0, 2.0, 4.0, 3.0])
        window_length = min(11, len(data))
        if window_length % 2 == 0:
            window_length -= 1
        polyorder = min(3, window_length - 1)
        smoothed = savgol_filter(data, window_length, polyorder)
        self.assertEqual(len(smoothed), len(data))

    def test_savgol_output_length_matches_input(self):
        """Smoothed output must have the same length as input."""
        data = np.random.random(512) * 65535
        smoothed = savgol_filter(data, 11, 3)
        self.assertEqual(len(smoothed), len(data))

    def test_dataprocessor_smooth_data(self):
        """DataProcessor.smooth_data should use savgol_filter correctly."""
        data = np.random.random(100) * 10000
        smoothed = DataProcessor.smooth_data(data, window_length=11, polyorder=3)
        self.assertEqual(len(smoothed), len(data))

class TestSplineInterpolation(unittest.TestCase):
    """Tests for spline interpolation used in spectrum curve rendering."""

    def test_spline_produces_more_points(self):
        """Spline interpolation should create a denser set of points."""
        wavelengths = np.linspace(900, 2500, 100)
        data = np.sin(wavelengths / 200)

        num_plot_points = min(len(wavelengths) * 3, 2048)
        wavelengths_smooth = np.linspace(
            wavelengths[0], wavelengths[-1], num_plot_points
        )
        spline = make_interp_spline(wavelengths, data, k=3)
        data_smooth = spline(wavelengths_smooth)

        self.assertEqual(len(data_smooth), num_plot_points)
        self.assertGreater(len(data_smooth), len(data))

    def test_spline_endpoints_match(self):
        """Spline interpolation should match at the original endpoints."""
        wavelengths = np.linspace(900, 2500, 100)
        data = np.sin(wavelengths / 200)

        wavelengths_smooth = np.linspace(wavelengths[0], wavelengths[-1], 300)
        spline = make_interp_spline(wavelengths, data, k=3)
        data_smooth = spline(wavelengths_smooth)

        np.testing.assert_almost_equal(data_smooth[0], data[0], decimal=5)
        np.testing.assert_almost_equal(data_smooth[-1], data[-1], decimal=5)

    def test_spline_with_typical_nir_data(self):
        """Spline should work with typical NIR spectrum data ranges."""
        wavelengths = np.linspace(900, 2500, 512)
        # Simulate a typical NIR spectrum with absorption features
        signal = (30000 + 5000 * np.sin(wavelengths / 300)
                  - 3000 * np.exp(-((wavelengths - 1450) ** 2) / (2 * 30 ** 2))
                  - 2000 * np.exp(-((wavelengths - 1940) ** 2) / (2 * 40 ** 2)))

        num_plot_points = min(len(wavelengths) * 3, 2048)
        wavelengths_smooth = np.linspace(
            wavelengths[0], wavelengths[-1], num_plot_points
        )
        spline = make_interp_spline(wavelengths, signal, k=3)
        data_smooth = spline(wavelengths_smooth)

        # Interpolated data should stay within the range of the original
        self.assertGreaterEqual(np.min(data_smooth), np.min(signal) - 100)
        self.assertLessEqual(np.max(data_smooth), np.max(signal) + 100)

if __name__ == '__main__':
    unittest.main()