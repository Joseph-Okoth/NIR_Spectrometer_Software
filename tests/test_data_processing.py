import unittest
import numpy as np
from backend.data_processing import process_data

class TestDataProcessing(unittest.TestCase):
    def test_process_data(self):
        wavelengths = np.linspace(900, 1700, 100)
        intensities = np.random.random(100)
        peaks = process_data(wavelengths, intensities)
        self.assertTrue(len(peaks) > 0)

if __name__ == '__main__':
    unittest.main()