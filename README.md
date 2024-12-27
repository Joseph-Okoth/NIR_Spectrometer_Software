# NIR Quest Software

NIR Quest Software is a user-friendly application designed for agricultural produce classification and prediction using Near-Infrared (NIR) spectroscopy. This software captures measurement procedures graphically, using drag-and-drop spectrometers, transform functions, and display nodes to automate unique post-processing workflows.

## Features
- Capture and process spectroscopy data
- Visualize data with interactive plots
- Classify agricultural produce using machine learning models
- Save and load measurement data
- User-friendly GUI built with PyQt5

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Joseph-Okoth/nir-quest-software.git
   cd nir-quest-software
   ```

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
nir_quest/
├── main.py              # Main application launcher
├── device_interface.py  # Module to handle communication with NIR Quest device
├── data_processing.py   # Module for processing spectral data
├── ml_models.py         # Module to handle ML-based classification and prediction
├── gui.py               # Module for the graphical user interface
├── utils.py             # Helper functions
└── requirements.txt     # Dependencies

```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Inspired by OceanView software
- Developed using Python and PyQt5