import unittest
from frontend.ui import SpectrumApp

class TestUI(unittest.TestCase):
    def test_ui_initialization(self):
        app = SpectrumApp()
        self.assertIsNotNone(app.build())

if __name__ == '__main__':
    unittest.main()