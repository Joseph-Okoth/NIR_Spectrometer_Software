import pandas as pd
import os
from datetime import datetime

def save_to_csv(wavelengths, intensities, filename="spectrum_data.csv"):
    """Save wavelength and intensity data to a CSV file."""
    data = {'Wavelength': wavelengths, 'Intensity': intensities}
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return True

def save_with_metadata(wavelengths, intensities, filename="spectrum_data.csv", 
                      metadata=None):
    """Save spectrum data with additional metadata."""
    data = {'Wavelength': wavelengths, 'Intensity': intensities}
    df = pd.DataFrame(data)
    
    # Add timestamp and metadata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', newline='') as f:
        # Write metadata header
        f.write(f"# Timestamp: {timestamp}\n")
        if metadata:
            for key, value in metadata.items():
                f.write(f"# {key}: {value}\n")
        f.write(f"# Points: {len(wavelengths)}\n")
        f.write(f"# Wavelength range: {min(wavelengths):.2f}-{max(wavelengths):.2f} nm\n")
        f.write(f"# Intensity range: {min(intensities)}-{max(intensities)}\n")
        f.write("#\n")
        
        # Write data
        df.to_csv(f, index=False)
    
    return True

def load_from_csv(filename):
    """Load spectrum data from a CSV file."""
    try:
        # First check if there's metadata
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        metadata = {}
        data_start = 0
        
        # Process metadata lines
        for i, line in enumerate(lines):
            if line.startswith('#'):
                if ':' in line:
                    key, value = line[1:].strip().split(':', 1)
                    metadata[key.strip()] = value.strip()
                data_start = i + 1
            else:
                break
        
        # Read the actual data
        df = pd.read_csv(filename, skiprows=data_start)
        wavelengths = df['Wavelength'].values
        intensities = df['Intensity'].values
        
        return wavelengths, intensities, metadata
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None, None, None

