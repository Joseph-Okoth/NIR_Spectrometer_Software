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
    usb.util.dispose_resources(usb_device)

def request_spectrum(usb_device, packet_size, spectra_epi, commands_epo):
    usb_send(usb_device, struct.pack('<B', command_set['SPECTR_REQUEST_SPECTRA']), epo=commands_epo)

    data = usb_read(usb_device, epi=spectra_epi, epi_size=packet_size)
    if len(data) == packet_size and data[packet_size - 1] == 0x69:
        spectrum = []
        for i in range(0, 4096, 2):
            databytes = [data[i], data[i + 1]]
            intval = int.from_bytes(databytes, byteorder='little')
            spectrum.append(intval)
        spectrum[1] = spectrum[0]
        return spectrum
    else:
        return 0

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