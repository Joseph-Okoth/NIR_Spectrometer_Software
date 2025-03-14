from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
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

        # Add top horizontal rectangles for icons
        self.add_widget(self.create_icon_bar())
        self.add_widget(self.create_icon_bar_2())

        # Flag to control measurement loop
        self.measuring = False

    def create_icon_bar(self):
        icon_bar = BoxLayout(size_hint=(1, 0.1))
        icons = [
            ('app_icon.svg', 'NIR Software', None),
            ('new_project.svg', 'Start Measurement', self.toggle_measurement),
            ('open.svg', 'Open File', self.open_file),
            ('run_n_pause.svg', 'Run/Pause', self.toggle_measurement)
        ]
        for icon, tooltip, callback in icons:
            btn = Button(background_normal=icon, size_hint=(0.25, 1))
            btn.tooltip = tooltip
            if callback is not None:  # Only bind if callback is not None
                btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def create_icon_bar_2(self):
        icon_bar = BoxLayout(size_hint=(1, 0.1))
        icons = [
            ('scale_to_fill_window.svg', 'Scale to Fill Window', self.scale_to_fill),
            ('zoom_into_graph.svg', 'Zoom In', self.zoom_in),
            ('zoom_out.svg', 'Zoom Out', self.zoom_out),
            ('panning.svg', 'Panning', self.panning),
            ('spectrum_overlay.svg', 'Spectrum Overlay', self.spectrum_overlay),
            ('delete.svg', 'Delete Spectrum', self.delete_spectrum),
            ('copy_data_to_clipboard.svg', 'Copy Data to Clipboard', self.copy_data),
            ('save_as_csv.svg', 'Save as CSV', self.save_as_csv),
            ('print_graph.svg', 'Print Graph', self.print_graph)
        ]
        for icon, tooltip, callback in icons:
            btn = Button(background_normal=icon, size_hint=(0.11, 1))
            btn.tooltip = tooltip
            btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def toggle_measurement(self, instance):
        if not self.measuring:
            self.measuring = True
            Clock.schedule_interval(self.collect_data, 0.5)  # Collect data every 0.5 seconds
        else:
            self.measuring = False
            Clock.unschedule(self.collect_data)

    def collect_data(self, dt):
        if self.spectrometer.usb_device:
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

    def open_file(self, instance):
        # Implement file opening logic here
        pass

    def scale_to_fill(self, instance):
        # Implement scaling logic here
        pass

    def zoom_in(self, instance):
        # Implement zoom in logic here
        pass

    def zoom_out(self, instance):
        # Implement zoom out logic here
        pass

    def panning(self, instance):
        # Implement panning logic here
        pass

    def spectrum_overlay(self, instance):
        # Implement spectrum overlay logic here
        pass

    def delete_spectrum(self, instance):
        # Implement delete spectrum logic here
        pass

    def copy_data(self, instance):
        # Implement copy data logic here
        pass

    def save_as_csv(self, instance):
        # Implement save as CSV logic here
        pass

    def print_graph(self, instance):
        # Implement print graph logic here
        pass

class SpectrumApp(App):
    def build(self):
        return MsainLayout()

    def on_stop(self):
        if hasattr(self.root, 'spectrometer'):
            drop_spectrometer(self.root.spectrometer.usb_device)