# NIR Spectrometer Software

NIR Spectrometer Software is a user-friendly application that captures measurement procedures graphically, using drag-and-drop spectrometers, transform functions, and display nodes to automate unique post-processing workflows. The software is also being designed for agricultural produce classification and prediction using Machine Learning technologies by analysis of the acquired data.
|
This software also enables the user to save the data obtained from the spectrometer in csv format for further analysis or reference purposes.
|
It is a free and open source alternative software for Ocean Optics Spectrometers.

## Features
- Capture and process spectroscopy data
- Visualize data with interactive plots
- Classify agricultural produce using machine learning models
- Save and load measurement data
- User-friendly GUI built with Kivy

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Joseph-Okoth/NIR-Spectrometer-Software.git
   cd NIR-Spectrometer-Software

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the application:

```bash
python main.py
```

### Features:
- **Start Measurement:** Capture spectroscopy data.
- **Save Data:** Save the captured data to a file.
- **Load Data:** Load previously saved data.
- **Plot Data:** Visualize the captured data.
- **Classify Produce:** Use machine learning models to classify agricultural produce.

## Project Structure
```
NIR_Spectrometer_Software/
│
├── README.md                   # Project description and instructions
├── requirements.txt            # List of Python dependencies
├── data_processing.py          # Code for data processing (Formula and Calculations)
├── utils.py                    # Code for Validating the formula and handling calculation errors
├── main.py                     # Entry point for the application
│
├── backend/                    # Backend logic (spectrometer communication, data processing)
│   ├── __init__.py
│   ├── spectrometer.py         # Code for spectrometer communication (updated from simple_spectrometer.py)
│   ├── data_processing.py      # Code for data processing (e.g., peak finding)
│   └── data_saving.py          # Code for saving data (e.g., CSV, JSON)
│
├── frontend/                   # Frontend logic (UI and visualization)
│   ├── __init__.py
│   ├── ui.py                   # Main UI layout and logic (using Kivy)
│   ├── icons/                  # Folder for icons (e.g., FontAwesome, Material Icons)
│   └── plots.py                # Code for plotting graphs
│
├── config/                     # Configuration files
│   ├── __init__.py
│   └── ocean_optics_configs.py # Spectrometer configurations (updated from ocean_optics_configs.py)
│
├── assets/                     # Static assets (e.g., images, fonts)
│   ├── icons/                  # Icons for buttons and UI elements
│   └── fonts/                  # Custom fonts (e.g., FontAwesome)
│
├── tests/                      # Unit and integration tests
│   ├── __init__.py
│   ├── test_spectrometer.py    # Tests for spectrometer communication
│   ├── test_data_processing.py # Tests for data processing
│   └── test_ui.py              # Tests for UI functionality
│
└── scripts/                    # Utility scripts (e.g., for deployment, data analysis)
    ├── deploy.sh               # Script to deploy the app
    └── analyze_data.py         # Script for additional data analysis
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request. Let's make a great application that we can easily access and have control over.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Inspired by OceanView software
- Developed using Python and Kivy