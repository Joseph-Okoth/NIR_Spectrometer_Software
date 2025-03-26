from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import csv
import numpy as np
from backend.spectrometer import find_spectrometer, request_spectrum, drop_spectrometer

# Custom FigureCanvasKivyAgg to handle resize_event and motion_notify_event
class CustomFigureCanvasKivyAgg(FigureCanvasKivyAgg):
    def __init__(self, figure, **kwargs):
        super().__init__(figure, **kwargs)
        self._is_drawn = False

    def resize_event(self):
        """Override resize_event to prevent errors."""
        if not self._is_drawn:
            self.draw()
            self._is_drawn = True

    def motion_notify_event(self, x, y, guiEvent=None):
        """Handle mouse motion events."""
        if hasattr(super(), 'motion_notify_event'):
            super().motion_notify_event(x, y, guiEvent)

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
        self.ax.set_title("Spectrum Window")

        # Add the Matplotlib figure to a Kivy widget
        self.canvas_widget = CustomFigureCanvasKivyAgg(self.fig)  # Use the custom class

        # Add top horizontal rectangles for icons
        self.icon_bar_1 = self.create_icon_bar()
        self.icon_bar_2 = self.create_icon_bar_2()

        # Add widgets to the main layout
        self.add_widget(self.icon_bar_1)
        self.add_widget(self.icon_bar_2)
        self.add_widget(self.canvas_widget)

        # Flag to control measurement loop
        self.measuring = False

    def create_icon_bar(self):
        """Create the first horizontal icon bar."""
        icon_bar = BoxLayout(size_hint=(1, None), height=50)  # Fixed height for the icon bar
        icons = [
            ('frontend/icons/app_icon.png', 'NIR Software', None, (50, 50)),  # Custom size (width, height)
            ('frontend/icons/new_project.png', 'Start Measurement', self.toggle_measurement, (50, 50)),
            ('frontend/icons/open.png', 'Open File', self.open_file, (50, 50)),
            ('frontend/icons/run_n_pause.png', 'Run/Pause', self.toggle_measurement, (25, 25))
        ]
        for icon, tooltip, callback, icon_size in icons:
            btn = Button(background_normal=icon, size_hint=(None, None), size=icon_size)
            btn.tooltip = tooltip
            if callback is not None:  # Only bind if callback is not None
                btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def create_icon_bar_2(self):
        """Create the second horizontal icon bar."""
        icon_bar = BoxLayout(size_hint=(None, None), height=40)  # Fixed height for the icon bar
        icons = [
            ('frontend/icons/scale_to_fill_window.png', 'Scale to Fill Window', self.scale_to_fill, (50, 50)),
            ('frontend/icons/zoom_into_graph.png', 'Zoom In', self.zoom_in, (50, 50)),
            ('frontend/icons/zoom_out.png', 'Zoom Out', self.zoom_out, (50, 50)),
            ('frontend/icons/panning.png', 'Panning', self.panning, (50, 50)),
            ('frontend/icons/spectrum_overlay.png', 'Spectrum Overlay', self.spectrum_overlay, (50, 50)),
            ('frontend/icons/delete.png', 'Delete Spectrum', self.delete_spectrum, (50, 50)),
            ('frontend/icons/copy_data_to_clipboard.png', 'Copy Data to Clipboard', self.copy_data, (50, 50)),
            ('frontend/icons/save_as_csv.png', 'Save as CSV', self.save_as_csv, (50, 50)),
            ('frontend/icons/print_graph.png', 'Print Graph', self.print_graph, (50, 50))
        ]
        for icon, tooltip, callback, icon_size in icons:
            btn = Button(background_normal=icon, size_hint=(None, None), size=icon_size)
            btn.tooltip = tooltip
            btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def toggle_measurement(self, instance):
        """Toggle the measurement loop."""
        if not self.measuring:
            self.measuring = True
            Clock.schedule_interval(self.collect_data, 0.5)  # Collect data every 0.5 seconds
        else:
            self.measuring = False
            Clock.unschedule(self.collect_data)

    def collect_data(self, dt):
        """Collect data from the spectrometer and update the plot."""
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
            self.ax.set_title("Spectrum Window")

            # Redraw the canvas to update the plot
            self.canvas_widget.draw()

    def open_file(self, instance):
        """Open a file dialog to load spectrum data."""
        file_chooser = FileChooserListView()
        popup = Popup(title='Open File', content=file_chooser, size_hint=(0.9, 0.9))
        file_chooser.bind(on_submit=lambda instance, value, _: self.load_file(value))
        popup.open()

    def load_file(self, file_path):
        """Load spectrum data from a file and plot it."""
        try:
            data = np.loadtxt(file_path, delimiter=',')
            self.ax.clear()
            self.ax.plot(data[:, 0], data[:, 1])
            self.ax.set_xlabel("Wavelength (nm)")
            self.ax.set_ylabel("Intensity")
            self.ax.set_title("Spectrum Window")
            self.canvas_widget.draw()
        except Exception as e:
            print(f"Error loading file: {e}")

    def scale_to_fill(self, instance):
        """Scale the plot to fill the window."""
        self.ax.autoscale()
        self.canvas_widget.draw()

    def zoom_in(self, instance):
        """Zoom into the plot."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] * 0.9, xlim[1] * 0.9)
        self.ax.set_ylim(ylim[0] * 0.9, ylim[1] * 0.9)
        self.canvas_widget.draw()

    def zoom_out(self, instance):
        """Zoom out of the plot."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] * 1.1, xlim[1] * 1.1)
        self.ax.set_ylim(ylim[0] * 1.1, ylim[1] * 1.1)
        self.canvas_widget.draw()

    def panning(self, instance):
        """Enable panning mode (to be implemented)."""
        pass

    def spectrum_overlay(self, instance):
        """Overlay multiple spectra (to be implemented)."""
        pass

    def delete_spectrum(self, instance):
        """Clear the current spectrum plot."""
        self.ax.clear()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity (counts)")
        self.ax.set_title("Spectrum Window")
        self.canvas_widget.draw()

    def copy_data(self, instance):
        """Copy the current spectrum data to the clipboard (to be implemented)."""
        pass

    def save_as_csv(self, instance):
        """Save the current spectrum data to a CSV file."""
        if hasattr(self, 'spectrum_data'):
            with open('spectrum_data.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Wavelength (nm)", "Intensity"])
                for i in range(len(self.spectrum_data)):
                    writer.writerow([i, self.spectrum_data[i]])

    def print_graph(self, instance):
        """Print the current graph (to be implemented)."""
        pass

class SpectrumApp(App):
    def build(self):
        return MainLayout()

    def on_stop(self):
        """Clean up resources when the app stops."""
        if hasattr(self.root, 'spectrometer'):
            drop_spectrometer(self.root.spectrometer.usb_device)

if __name__ == '__main__':
    SpectrumApp().run()



    