import unittest
from backend.spectrometer import find_spectrometer

class TestSpectrometer(unittest.TestCase):
    def test_find_spectrometer(self):
        spectrometer = find_spectrometer()
        self.assertIsNotNone(spectrometer.usb_device)

if __name__ == '__main__':
    unittest.main()