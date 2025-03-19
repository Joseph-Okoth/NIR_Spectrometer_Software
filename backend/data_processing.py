import numpy as np
from scipy.signal import find_peaks

def process_data(wavelengths, intensities):
    peaks, _ = find_peaks(intensities, height=1000)
    return wavelengths[peaks]

