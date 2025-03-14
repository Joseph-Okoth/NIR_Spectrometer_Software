from frontend.ui import SpectrumApp
# import usb.backend.libusb1
# import usb.core

# # Set the libusb backend
# backend = usb.backend.libusb1.get_backend()
# usb.core.find(backend=backend)

# # Find all USB devices
# devices = usb.core.find(find_all=True)
# for device in devices:
#     print(device)

if __name__ == '__main__':
    SpectrumApp().run()