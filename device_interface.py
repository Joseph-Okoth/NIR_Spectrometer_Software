import usb.core
import usb.util
import numpy as np

class NIRDevice:
    def __init__(self):
        self.device = None

    def connect(self):
        self.device = usb.core.find(idVendor=0x1234, idProduct=0x5678)  # Replace with actual Vendor/Product ID
        if self.device is None:
            raise ValueError("NIR Quest device not found!")
        self.device.set_configuration()

    def capture_data(self):
        try:
            raw_data = self.device.read(0x81, 1024)  # Example endpoint
            return np.array(raw_data)
        except usb.core.USBError as e:
            print("Error reading data:", e)
            return None

    def release(self):
        usb.util.dispose_resources(self.device)
