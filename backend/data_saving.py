import pandas as pd

def save_to_csv(wavelengths, intensities, filename="spectrum_data.csv"):
    data = {'Wavelength': wavelengths, 'Intensity': intensities}
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)