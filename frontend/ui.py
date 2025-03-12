from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import numpy as np
from backend.spectrometer import find_spectrometer, request_spectrum, drop_spectrometer

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Add a plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasKivyAgg(self.fig)
        self.add_widget(self.canvas)

        # Add buttons
        self.btn_collect = Button(text="Collect Data", size_hint=(1, 0.1))
        self.btn_collect.bind(on_press=self.collect_data)
        self.add_widget(self.btn_collect)

        self.btn_save = Button(text="Save Data", size_hint=(1, 0.1))
        self.add_widget(self.btn_save)

        # Initialize spectrometer
        self.spectrometer = find_spectrometer()

    def collect_data(self, instance):
        if self.spectrometer.usb_device:
            acquired = request_spectrum(self.spectrometer.usb_device, self.spectrometer.packet_size,
                                       self.spectrometer.spectra_ep_in, self.spectrometer.cmd_ep_out)
            self.ax.clear()
            self.ax.plot(acquired)
            self.ax.set_xlabel("Wavelength (nm)")
            self.ax.set_ylabel("Intensity")
            self.ax.set_title("NIR Spectrum")
            self.canvas.draw()

class SpectrumApp(App):
    def build(self):
        return MainLayout()

    def on_stop(self):
        if hasattr(self.root, 'spectrometer'):
            drop_spectrometer(self.root.spectrometer.usb_device)