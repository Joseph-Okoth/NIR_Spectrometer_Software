# Code Citations

## License: Apache-2.0
https://github.com/snatch59/simple-ocean-optics-spectrometer/blob/5caa64cb2a859fb8d27755787c156b5daa5e16e6/simple_spectrometer.py

```
if len(data) == packet_size and data[packet_size - 1] == 0x69:
        spectrum = []
        for i in range(0, 4096, 2):
            databytes = [data[i], data[i + 1]]
            intval = int.from_bytes(databytes, byteorder='little')
            spectrum.append(
```

