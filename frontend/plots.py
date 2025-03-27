import matplotlib.pyplot as plt

def plot_spectrum(wavelengths, intensities):
    plt.plot(wavelengths, intensities)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (counts)")
    plt.title("Spectrum Window")
    plt.show()