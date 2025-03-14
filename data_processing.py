import numpy as np
from scipy.signal import savgol_filter
from utils import validate_formula, calculate_custom

class DataProcessor:
    @staticmethod
    def smooth_data(data, window_length=11, polyorder=3):
        return savgol_filter(data, window_length, polyorder)

    @staticmethod
    def normalize_data(data):
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    @staticmethod
    def baseline_correction(data, degree=2):
        coeffs = np.polyfit(np.arange(len(data)), data, degree)
        baseline = np.polyval(coeffs, np.arange(len(data)))
        return data - baseline

    @staticmethod
    def apply_formula(data, formula):
        validate_formula(formula)  # Ensure formula safety
        return calculate_custom(data, formula)

    @staticmethod
    def extract_features(data):
        return {
            "max_intensity": np.max(data),
            "mean_intensity": np.mean(data),
        }
