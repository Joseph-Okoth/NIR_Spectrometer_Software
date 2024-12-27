import os
import numpy as np

def save_data_to_file(data, filename):
    """Save spectral data to a file."""
    if not filename.endswith('.csv'):
        filename += '.csv'
    np.savetxt(filename, data, delimiter=',', header='Wavelength,Intensity')
    print(f"Data saved to {filename}")

def load_data_from_file(filename):
    """Load spectral data from a file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    data = np.loadtxt(filename, delimiter=',', skiprows=1)
    print(f"Data loaded from {filename}")
    return data

def validate_formula(formula):
    """Validate a mathematical formula string for safe evaluation."""
    allowed_chars = "0123456789.+-*/()np •sqrt"
    if all(c in allowed_chars for c in formula):
        return True
    raise ValueError("Invalid characters in formula. Only basic math operations are allowed.")

def calculate_custom(data, formula):
    """Apply a custom formula to the spectral data."""
    validate_formula(formula)
    result = eval(formula, {"np": np}, {"data": data})
    return result

def format_output(data):
    """Format output for display."""
    return "\n".join([f"{row[0]:.2f}, {row[1]:.2f}" for row in data])
