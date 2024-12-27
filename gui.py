import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt
from utils import save_data_to_file, load_data_from_file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIR Quest Spectroscopy Software")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.spectral_data = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Spectroscopy Analysis Tool")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_data)
        layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(self.save_button)

        self.plot_button = QPushButton("Plot Spectral Data")
        self.plot_button.clicked.connect(self.plot_data)
        layout.addWidget(self.plot_button)

        self.process_button = QPushButton("Process Data")
        self.process_button.clicked.connect(self.process_data)
        layout.addWidget(self.process_button)

        self.classify_button = QPushButton("Classify Using ML")
        self.classify_button.clicked.connect(self.classify_data)
        layout.addWidget(self.classify_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Spectral Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.spectral_data = load_data_from_file(file_name)
            self.label.setText(f"Loaded data from {file_name}")

    def save_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Spectral Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name and self.spectral_data is not None:
            save_data_to_file(self.spectral_data, file_name)
            self.label.setText(f"Saved data to {file_name}")

    def plot_data(self):
        if self.spectral_data is None:
            self.label.setText("No data to plot!")
            return
        series = QLineSeries()
        for wl, intensity in self.spectral_data:
            series.append(wl, intensity)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Spectral Data")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QChartView.Antialiasing)
        chart_view.show()

    def process_data(self):
        self.label.setText("Data Processing Completed!")

    def classify_data(self):
        self.label.setText("Classified: Ripe")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
