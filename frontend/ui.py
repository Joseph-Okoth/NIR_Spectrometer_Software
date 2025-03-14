from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from backend.spectrometer import find_spectrometer, request_spectrum, drop_spectrometer

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Initialize spectrometer
        self.spectrometer = find_spectrometer()

        # Create a Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity")
        self.ax.set_title("NIR Spectrum")

        # Add the Matplotlib figure to a Kivy widget
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        self.add_widget(self.canvas_widget)

        # Add buttons
        self.btn_collect = Button(text="Start Measurement", size_hint=(1, 0.1))
        self.btn_collect.bind(on_press=self.toggle_measurement)
        self.add_widget(self.btn_collect)

        self.btn_save = Button(text="Save Data", size_hint=(1, 0.1))
        self.add_widget(self.btn_save)

        # Flag to control measurement loop
        self.measuring = False

    def toggle_measurement(self, instance):
        if not self.measuring:
            self.measuring = True
            self.btn_collect.text = "Stop Measurement"
            Clock.schedule_interval(self.collect_data, 0.5)  # Collect data every 0.5 seconds
        else:
            self.measuring = False
            self.btn_collect.text = "Start Measurement"
            Clock.unschedule(self.collect_data)

    def collect_data(self, dt):
        if self.spectrometer.usb_device:
            # Request spectrum data from the spectrometer
            acquired = request_spectrum(
                self.spectrometer.usb_device,
                self.spectrometer.packet_size,
                self.spectrometer.spectra_ep_in,
                self.spectrometer.cmd_ep_out
            )

            # Clear the previous plot and plot the new data
            self.ax.clear()
            self.ax.plot(acquired)
            self.ax.set_xlabel("Wavelength (nm)")
            self.ax.set_ylabel("Intensity")
            self.ax.set_title("NIR Spectrum")

            # Redraw the canvas to update the plot
            self.canvas_widget.draw()

class SpectrumApp(App):
    def build(self):
        return MainLayout()

    def on_stop(self):
        # Clean up spectrometer resources when the app is closed
        if hasattr(self.root, 'spectrometer'):
            drop_spectrometer(self.root.spectrometer.usb_device)