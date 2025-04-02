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
        
        # Grid settings
        self.grid_enabled = True
        self.grid_style = {'color': 'lightgray', 'linestyle': '--', 'alpha': 0.7}
        self.major_grid_style = {'color': 'gray', 'linestyle': '-', 'alpha': 0.5}

        # Initialize spectrometer
        self.spectrometer = find_spectrometer()

        # Initialize wavelength array for NIR-Quest (900-2500 nm range)
        num_pixels = 4096  # NIR-Quest typical pixel count
        self.wavelengths = np.linspace(900, 2500, num_pixels)  # Create wavelength array
        self.spectrum_data = None

        # Create a Matplotlib figure with specific size and DPI
        self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi=100)
        self._setup_plot()

        # Add the Matplotlib figure to a Kivy widget
        self.canvas_widget = CustomFigureCanvasKivyAgg(self.fig)

        # Add top horizontal rectangles for icons
        self.icon_bar_1 = self.create_icon_bar()
        self.icon_bar_2 = self.create_icon_bar_2()

        # Add widgets to the main layout
        self.add_widget(self.icon_bar_1)
        self.add_widget(self.icon_bar_2)
        self.add_widget(self.canvas_widget)

        # Flag to control measurement loop
        self.measuring = False

    def _update_grid(self):
        """Update gridlines based on current settings."""
        self.ax.grid(self.grid_enabled, which='both', **self.grid_style)
        self.ax.grid(self.grid_enabled, which='major', **self.major_grid_style)
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.draw()

    def _setup_plot(self):
        """Initialize plot with proper settings and gridlines."""
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity (counts)")
        self.ax.set_title("NIR Spectrum")
        
        # Set the x-axis range to match NIR-Quest specifications
        self.ax.set_xlim(900, 2500)
        
        # Add minor gridlines for better readability
        self.ax.minorticks_on()
        self._update_grid()

    def create_icon_bar(self):
        """Create the first horizontal icon bar."""
        icon_bar = BoxLayout(size_hint=(None, None), height=50)
        icons = [
            ('frontend/icons/app_icon.png', 'NIR Software', None, (50, 50)),
            ('frontend/icons/new_project.png', 'Start Measurement', self.toggle_measurement, (50, 50)),
            ('frontend/icons/open.png', 'Open File', self.open_file, (50, 50)),
            ('frontend/icons/run_n_pause.png', 'Run/Pause', self.toggle_measurement, (50, 50))
        ]
        for icon, tooltip, callback, icon_size in icons:
            btn = Button(background_normal=icon, size_hint=(None, None), size=icon_size)
            btn.tooltip = tooltip
            if callback is not None:
                btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def create_icon_bar_2(self):
        """Create the second horizontal icon bar with additional grid controls."""
        icon_bar = BoxLayout(size_hint=(None, None), height=55)
        icons = [
            ('frontend/icons/scale_to_fill_window.png', 'Scale to Fill Window', self.scale_to_fill, (50, 50)),
            ('frontend/icons/zoom_into_graph.png', 'Zoom In', self.zoom_in, (50, 50)),
            ('frontend/icons/zoom_out.png', 'Zoom Out', self.zoom_out, (50, 50)),
            ('frontend/icons/grid.png', 'Toggle Grid', self.toggle_grid, (50, 50)),
            ('frontend/icons/panning.png', 'Panning', self.panning, (45, 45)),
            ('frontend/icons/spectrum_overlay.png', 'Spectrum Overlay', self.spectrum_overlay, (45, 45)),
            ('frontend/icons/delete.png', 'Delete Spectrum', self.delete_spectrum, (45, 45)),
            ('frontend/icons/copy_data_to_clipboard.png', 'Copy Data to Clipboard', self.copy_data, (40, 40)),
            ('frontend/icons/save_as_csv.png', 'Save as CSV', self.save_as_csv, (45, 45)),
            ('frontend/icons/print_graph.png', 'Print Graph', self.print_graph, (40, 40))
        ]
        for icon, tooltip, callback, icon_size in icons:
            btn = Button(background_normal=icon, size_hint=(None, None), size=icon_size)
            btn.tooltip = tooltip
            btn.bind(on_press=callback)
            icon_bar.add_widget(btn)
        return icon_bar

    def toggle_grid(self, instance):
        """Toggle grid visibility."""
        self.grid_enabled = not self.grid_enabled
        self._update_grid()

    def toggle_measurement(self, instance):
        """Toggle the measurement loop."""
        if not self.measuring:
            self.measuring = True
            Clock.schedule_interval(self.collect_data, 0.5)
        else:
            self.measuring = False
            Clock.unschedule(self.collect_data)

    def collect_data(self, dt):
        """Collect data from the spectrometer and update the plot."""
        if not self.spectrometer.usb_device:
            print("No spectrometer device found")
            return

        print("Acquiring spectrum data...")
        acquired = request_spectrum(
            self.spectrometer.usb_device,
            self.spectrometer.packet_size,
            self.spectrometer.spectra_ep_in,
            self.spectrometer.cmd_ep_out
        )
        
        if acquired:
            print(f"Data received - Length: {len(acquired)}")
            print(f"First few values: {acquired[:5]}")
            
            # Ensure wavelengths and spectrum data have same length
            if len(acquired) != len(self.wavelengths):
                print(f"Length mismatch: wavelengths ({len(self.wavelengths)}) vs spectrum ({len(acquired)})")
                return
                
            self.spectrum_data = acquired
            
            try:
                # Clear the previous plot
                self.ax.clear()
                
                # Plot with proper formatting and check data ranges
                min_intensity = min(self.spectrum_data)
                max_intensity = max(self.spectrum_data)
                print(f"Intensity range: {min_intensity} to {max_intensity}")
                
                self.ax.plot(self.wavelengths, self.spectrum_data, 'b-', linewidth=1.5, label='Spectrum')
                
                # Set y-axis limits with some padding
                self.ax.set_ylim(min_intensity * 0.9, max_intensity * 1.1)
                
                # Add legend and grid
                self.ax.legend(loc='upper right')
                
                # Reapply the plot settings
                self._setup_plot()
                
                # Force redraw
                self.fig.tight_layout()
                self.canvas_widget.draw()
                
                print("Plot updated successfully")
            except Exception as e:
                print(f"Error plotting data: {e}")
        else:
            print("Failed to acquire spectrum data")

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
            self._setup_plot()  # Reapply grid and labels
            self.canvas_widget.draw()
        except Exception as e:
            print(f"Error loading file: {e}")

    def scale_to_fill(self, instance):
        """Scale the plot to fill the window."""
        self.ax.autoscale()
        self._update_grid()
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
        """Enable panning mode."""
        pass

    def spectrum_overlay(self, instance):
        """Overlay multiple spectra."""
        pass

    def delete_spectrum(self, instance):
        """Clear the current spectrum plot."""
        self.ax.clear()
        self._setup_plot()  # Reapply grid and labels
        self.canvas_widget.draw()

    def copy_data(self, instance):
        """Copy the current spectrum data to the clipboard (to be implemented)."""
        pass

    def save_as_csv(self, instance):
        """Save the current spectrum data to a CSV file."""
        if hasattr(self, 'spectrum_data') and self.spectrum_data is not None:
            with open('spectrum_data.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Wavelength (nm)", "Intensity"])
                for i, intensity in enumerate(self.spectrum_data):
                    writer.writerow([self.wavelengths[i], intensity])

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

