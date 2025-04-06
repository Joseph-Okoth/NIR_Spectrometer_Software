import usb.core
import usb.util
import struct
from collections import namedtuple
from config.ocean_optics_configs import vendor_ids, model_configs, end_points, command_set

# Definition of global named tuples in use
Profile = namedtuple('Profile', 'usb_device, device_id, model_name, packet_size, cmd_ep_out, data_ep_in, '
                                'data_ep_in_size, spectra_ep_in, spectra_ep_in_size')

def find_spectrometer():
    spectrometer_profile = Profile(usb_device=None, device_id=None, model_name='unknown', packet_size=0,
                                   cmd_ep_out=0, data_ep_in=0, data_ep_in_size=0, spectra_ep_in=0, spectra_ep_in_size=0)

    # Find any vendor devices
    usb_devices = usb.core.find(find_all=True, idVendor=vendor_ids['OCEANOPTICS_VENDOR'])

    if usb_devices is None:
        raise ValueError('No Vendor Spectrometers found')

    # Load the Ocean Optics spectrometer configurations
    ModelConfigs = namedtuple('ModelConfigs', 'device_ids, model_name, packet_size, cmd_epo, data_epi, data_epi_size, '
                                              'spect_epi, spect_epi_size')
    spectrometers = list(map(ModelConfigs._make, model_configs))

    # We've found one or more spectrometers
    for _usb_device in usb_devices:
        print('Product Id: ' + hex(_usb_device.idProduct))

        # Find device id in product_configs (we only use the first spectrometer found)
        spectrometer = [item for item in spectrometers for id in item.device_ids if id == _usb_device.idProduct]
        if spectrometer:
            # Load in its configuration
            spectrometer_profile = spectrometer_profile._replace(
                usb_device=_usb_device,
                device_id=_usb_device.idProduct,
                model_name=spectrometer[0].model_name,
                packet_size=spectrometer[0].packet_size,
                cmd_ep_out=spectrometer[0].cmd_epo,
                data_ep_in=spectrometer[0].data_epi,
                data_ep_in_size=spectrometer[0].data_epi_size,
                spectra_ep_in=spectrometer[0].spect_epi,
                spectra_ep_in_size=spectrometer[0].spect_epi_size
            )
            print(spectrometer_profile.model_name, 'found ...')

            # Use and set USB configuration for first spectrometer found
            _usb_device.set_configuration()
            break

    return spectrometer_profile

def drop_spectrometer(usb_device):
    """Release resources for the spectrometer."""
    if usb_device is None:
        print("No USB device to release.")
        return  # Safely exit if usb_device is None

    try:
        usb.util.dispose_resources(usb_device)
        print("USB resources released successfully.")
    except Exception as e:
        print(f"Error releasing USB resources: {e}")

def request_spectrum(usb_device, packet_size, spectra_epi, commands_epo):
    """Request and read spectrum data from the spectrometer."""
    try:
        # Send spectrum request command
        print("Sending spectrum request command...")
        usb_send(usb_device, struct.pack('<B', command_set['SPECTR_REQUEST_SPECTRA']), epo=commands_epo)
        
        # Read the response data - use dynamic buffer size
        received_data = usb_read(usb_device, epi=spectra_epi, epi_size=packet_size)
        actual_size = len(received_data)
        print(f"Received {actual_size} bytes")
        
        if not received_data:
            print("No data received from spectrometer")
            return None
            
        # Check for end marker - should be 0x69 at the end
        if actual_size > 0 and received_data[actual_size - 1] != 0x69:
            print("Invalid end marker in data")
            return None
            
        # Process the spectrum data with actual received size
        spectrum = []
        # Process 16-bit intensity values (2 bytes per point)
        for i in range(0, actual_size-1, 2):
            if i+1 < actual_size:
                intensity = struct.unpack('<H', bytes([received_data[i], received_data[i+1]]))[0]
                spectrum.append(intensity)
        
        print(f"Successfully processed spectrum with {len(spectrum)} points")
        return spectrum
        
    except Exception as e:
        print(f"Error in request_spectrum: {e}")
        return None

def usb_send(usb_device, data, epo=None):
    if epo is None:
        epo = end_points['EP1_OUT']
    usb_device.write(epo, data)

def usb_read(usb_device, epi=None, epi_size=None):
    if epi is None:
        epi = end_points['EP2_IN']
    if epi_size is None:
        epi_size = 512
    return usb_device.read(epi, epi_size)

def process_spectrum(data):
    """Convert raw spectral data bytes to intensity values for NIR-Quest."""
    try:
        spectrum = []
        # Process 16-bit intensity values (NIR-Quest uses 16-bit ADC)
        for i in range(0, len(data)-1, 2):
            intensity = struct.unpack('<H', data[i:i+2])[0]
            spectrum.append(intensity)
            
        # Verify we got the expected number of points (4096 for NIR-Quest)
        if len(spectrum) != 4096:
            print(f"Warning: Expected 4096 points, got {len(spectrum)}")
            
        # Basic data validation
        if max(spectrum) == 0:
            print("Warning: All intensity values are zero")
        elif max(spectrum) >= 65535:
            print("Warning: Intensity values may be saturated")
            
        return spectrum
        
    except Exception as e:
        print(f"Error processing spectrum: {e}")
        return None



