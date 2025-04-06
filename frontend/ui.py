from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
import matplotlib.pyplot as plt
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import csv
import numpy as np
import os
from backend.spectrometer import find_spectrometer, request_spectrum, drop_spectrometer
from backend.data_saving import save_to_csv, save_with_metadata, load_from_csv
from frontend.matplotlib_widget import MatplotlibWidget
from frontend.custom_widgets import IconButton
from kivy.graphics import Color, Rectangle

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Ensure we're in the right directory for icon loading
        print(f"Current working directory: {os.getcwd()}")
        
        # Verify icon paths
        self.verify_icons = True  # Set to True to enable detailed icon debugging
        if self.verify_icons:
            print("Checking for icon directories...")
            if not os.path.exists("frontend"):
                print("WARNING: 'frontend' directory not found!")
            if not os.path.exists("frontend/icons"):
                print("WARNING: 'frontend/icons' directory not found!")
            else:
                print(f"frontend/icons directory exists and contains: {os.listdir('frontend/icons')}")
        
        # Grid settings
        self.grid_enabled = True
        self.grid_style = {'color': 'lightgray', 'linestyle': '--', 'alpha': 0.7}
        self.major_grid_style = {'color': 'gray', 'linestyle': '-', 'alpha': 0.5}

        # Initialize spectrometer
        self.spectrometer = find_spectrometer()
        
        # Get wavelength range based on spectrometer model
        self.wavelength_start = 900
        self.wavelength_end = 2500
        
        # Adjust range if we know the spectrometer model
        if hasattr(self.spectrometer, 'model_name'):
            model = self.spectrometer.model_name
            print(f"Detected spectrometer model: {model}")
            # You could have different ranges based on model
            if "NIR" in model or "NIRQUEST" in model:
                self.wavelength_start = 900
                self.wavelength_end = 2500
            elif "USB2000" in model:
                self.wavelength_start = 200
                self.wavelength_end = 850
        
        # Initialize wavelength array and spectrum data
        self.num_pixels = 512  # Will be adjusted based on actual data received
        self.wavelengths = np.linspace(self.wavelength_start, self.wavelength_end, self.num_pixels)
        self.spectrum_data = None
        self.measuring = False
        
        # Signal averaging settings
        self.scans_to_average = 10  # Default value, can be adjusted by user
        self.averaging_enabled = True
        
        # Correction spectra
        self.dark_spectrum = None
        self.reference_spectrum = None
        self.use_dark_correction = True
        self.use_reference_correction = False  # Enables reflectance mode when True
        
        # Create a matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        # Create our custom MatplotlibWidget with the figure
        self.plot_widget = MatplotlibWidget(figure=self.fig)
        
        # Setup plot AFTER creating plot_widget
        self._setup_plot()
        
        # Initialize with empty plot
        self.initialize_empty_plot()
        
        # Create icon bars with simpler setup
        icon_bar1 = self.create_icon_bar()
        icon_bar1.size_hint_y = None
        icon_bar1.height = 60
        icon_bar1.padding = [5, 5, 5, 5]
        icon_bar1.spacing = 5
        icon_bar1.orientation = 'horizontal'
        icon_bar1.canvas.before.clear()
        with icon_bar1.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Very light gray
            Rectangle(pos=icon_bar1.pos, size=icon_bar1.size)
        icon_bar1.bind(pos=self._update_bar_bg, size=self._update_bar_bg)

        icon_bar2 = self.create_icon_bar_2()
        icon_bar2.size_hint_y = None
        icon_bar2.height = 60
        icon_bar2.padding = [5, 5, 5, 5]
        icon_bar2.spacing = 5
        icon_bar2.orientation = 'horizontal'
        icon_bar2.canvas.before.clear()
        with icon_bar2.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Very light gray
            Rectangle(pos=icon_bar2.pos, size=icon_bar2.size)
        icon_bar2.bind(pos=self._update_bar_bg, size=self._update_bar_bg)

        # Create a status bar
        status_bar = BoxLayout(size_hint=(1, None), height=30)
        status_label = Label(text="NIR Spectrometer Software - Ready", size_hint=(1, 1))
        status_bar.add_widget(status_label)
        self.add_widget(status_bar)

        self.check_icon_paths()

        # Add all widgets to the main layout in the correct order (top to bottom)
        self.clear_widgets()  # Clear any existing widgets
        self.add_widget(icon_bar1)  # First toolbar at top
        self.add_widget(icon_bar2)  # Second toolbar below first
        self.add_widget(self.plot_widget)  # Plot in the middle (takes most space)
        self.add_widget(status_bar)  # Status bar at bottom

    def _update_grid(self):
        """Update gridlines based on current settings."""
        self.ax.grid(self.grid_enabled, which='both', **self.grid_style)
        self.ax.grid(self.grid_enabled, which='major', **self.major_grid_style)
        self.plot_widget.draw()

    def _setup_plot(self):
        """Initialize plot with proper settings and gridlines."""
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Reflectance (%)")  # Changed from "Intensity (counts)"
        self.ax.set_title("NIR Spectrum")
        
        # Set the x-axis range based on wavelength data
        if hasattr(self, 'wavelengths') and len(self.wavelengths) > 0:
            x_min = min(self.wavelengths)
            x_max = max(self.wavelengths)
            # Add a margin on both sides for better visibility 
            margin = (x_max - x_min) * 0.05
            self.ax.set_xlim(x_min - margin, x_max + margin)
        
        # Add minor gridlines for better readability
        self.ax.minorticks_on()
        
        # Improve plot distribution
        # Adjust subplot parameters to give the plot more room
        self.fig.subplots_adjust(left=0.1, right=0.95, bottom=0.12, top=0.9)
        
        # Update grid
        self._update_grid()

    def initialize_empty_plot(self):
        """Set up an empty plot with proper formatting when no data is available yet."""
        print("Initializing empty plot...")
        self.ax.clear()
        self.ax.set_xlim(self.wavelength_start, self.wavelength_end)
        self.ax.set_ylim(0, 100)  # Reflectance range 0-100%
        
        # Make sure the background is white for visibility
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        
        # Add an informative text
        self.ax.text(
            (self.wavelength_start + self.wavelength_end) / 2, 
            50, 
            "No spectrum data\nPress 'Start Measurement' to begin", 
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12
        )
        
        # Set axis labels
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Reflectance (%)")
        self.ax.set_title("NIR Spectrum")
        
        # Apply tight layout to ensure everything is visible
        self.fig.tight_layout()
        
        # Force redraw
        self.plot_widget.draw()
        print("Empty plot initialized")

    def create_icon_bar(self):
        """Create the main icon bar with icons and tooltips."""
        icon_bar = BoxLayout(size_hint=(1, None), height=60, spacing=5, padding=[5, 5, 5, 0])
        
        # App icon (not clickable)
        app_icon = IconButton(
            icon_source='frontend/icons/app_icon.png', 
            tooltip_text='NIR Spectrometer Software',
            size_hint=(1, 1)
        )
        
        # Start/Stop measurement button
        self.start_button = IconButton(
            icon_source='frontend/icons/new_project.png',
            tooltip_text='Start/Stop Measurement',
            size_hint=(1, 1)
        )
        self.start_button.bind(on_press=self.toggle_measurement)
        
        # Open file button
        open_button = IconButton(
            icon_source='frontend/icons/open.png',
            tooltip_text='Open Spectrum File',
            size_hint=(1, 1)
        )
        open_button.bind(on_press=self.open_file)
        
        # Run/Pause continuous acquisition
        run_pause_button = IconButton(
            icon_source='frontend/icons/run_n_pause.png',
            tooltip_text='Run/Pause Continuous Mode',
            size_hint=(1, 1)
        )
        run_pause_button.bind(on_press=self.toggle_continuous_mode)
        
        # Dark spectrum button
        dark_button = IconButton(
            icon_source='frontend/icons/dark_mode.png',  # You'll need this icon
            tooltip_text='Collect Dark Spectrum',
            size_hint=(1, 1)
        )
        dark_button.bind(on_press=self.collect_dark_spectrum)
        
        # Reference spectrum button
        ref_button = IconButton(
            icon_source='frontend/icons/reference.png',
            tooltip_text='Collect Reference Spectrum',
            size_hint=(1, 1)
        )
        ref_button.bind(on_press=self.collect_reference_spectrum)
        
        # Add all buttons to the icon bar
        icon_bar.add_widget(app_icon)
        icon_bar.add_widget(self.start_button)
        icon_bar.add_widget(open_button)
        icon_bar.add_widget(run_pause_button)
        icon_bar.add_widget(dark_button)
        icon_bar.add_widget(ref_button)
        
        return icon_bar

    def create_icon_bar_2(self):
        """Create the secondary icon bar with icons and tooltips."""
        icon_bar = BoxLayout(size_hint=(1, None), height=60, spacing=5, padding=[5, 5, 5, 0])
        
        # Scale to fill
        scale_button = IconButton(
            icon_source='frontend/icons/scale_to_fill_window.png',
            tooltip_text='Scale to Fill Window',
            size_hint=(1, 1)
        )
        scale_button.bind(on_press=self.scale_to_fill)
        
        # Zoom in
        zoom_in_button = IconButton(
            icon_source='frontend/icons/zoom_into_graph.png',
            tooltip_text='Zoom In',
            size_hint=(1, 1)
        )
        zoom_in_button.bind(on_press=self.zoom_in)
        
        # Zoom out
        zoom_out_button = IconButton(
            icon_source='frontend/icons/zoom_out.png',
            tooltip_text='Zoom Out',
            size_hint=(1, 1)
        )
        zoom_out_button.bind(on_press=self.zoom_out)
        
        # Panning
        panning_button = IconButton(
            icon_source='frontend/icons/panning.png',
            tooltip_text='Enable Panning Mode',
            size_hint=(1, 1)
        )
        panning_button.bind(on_press=self.panning)
        
        # Spectrum overlay
        overlay_button = IconButton(
            icon_source='frontend/icons/spectrum_overlay.png',
            tooltip_text='Toggle Spectrum Overlay',
            size_hint=(1, 1)
        )
        overlay_button.bind(on_press=self.spectrum_overlay)
        
        # Delete spectrum
        delete_button = IconButton(
            icon_source='frontend/icons/delete.png',
            tooltip_text='Delete Current Spectrum',
            size_hint=(1, 1)
        )
        delete_button.bind(on_press=self.delete_spectrum)
        
        # Copy data
        copy_button = IconButton(
            icon_source='frontend/icons/copy_data_to_clipboard.png',
            tooltip_text='Copy Data to Clipboard',
            size_hint=(1, 1)
        )
        copy_button.bind(on_press=self.copy_data)
        
        # Save as CSV
        save_button = IconButton(
            icon_source='frontend/icons/save_as_csv.png',
            tooltip_text='Save as CSV',
            size_hint=(1, 1)
        )
        save_button.bind(on_press=self.save_as_csv)
        
        # Print graph
        print_button = IconButton(
            icon_source='frontend/icons/print_graph.png',
            tooltip_text='Print Graph',
            size_hint=(1, 1)
        )
        print_button.bind(on_press=self.print_graph)
        
        # Add all buttons to the icon bar
        icon_bar.add_widget(scale_button)
        icon_bar.add_widget(zoom_in_button)
        icon_bar.add_widget(zoom_out_button)
        icon_bar.add_widget(panning_button)
        icon_bar.add_widget(overlay_button)
        icon_bar.add_widget(delete_button)
        icon_bar.add_widget(copy_button)
        icon_bar.add_widget(save_button)
        icon_bar.add_widget(print_button)
        
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

    def toggle_continuous_mode(self, instance):
        """Toggle continuous measurement mode."""
        if not hasattr(self, 'continuous_mode'):
            self.continuous_mode = False
        
        self.continuous_mode = not self.continuous_mode
        
        if self.continuous_mode:
            # Start continuous measurement with faster refresh
            Clock.schedule_interval(self.collect_data, 0.2)  # 5 times per second
            print("Continuous mode enabled")
        else:
            # Stop continuous measurement
            Clock.unschedule(self.collect_data)
            print("Continuous mode disabled")

    def collect_data(self, dt):
        """Collect data from the spectrometer with improved noise reduction."""
        if not self.spectrometer.usb_device:
            print("No spectrometer device found")
            return

        print("Acquiring spectrum data...")
        
        # Collect multiple scans for averaging
        scan_count = self.scans_to_average if self.averaging_enabled else 1
        collected_scans = []
        
        for i in range(scan_count):
            acquired = request_spectrum(
                self.spectrometer.usb_device,
                self.spectrometer.packet_size,
                self.spectrometer.spectra_ep_in,
                self.spectrometer.cmd_ep_out
            )
            if acquired:
                collected_scans.append(acquired)
                if i % 2 == 0:  # Update progress every 2 scans
                    print(f"Collecting scan {i+1}/{scan_count}")
        
        if collected_scans:
            # Average the scans to reduce noise
            raw_data = np.mean(collected_scans, axis=0)
            print(f"Averaged {len(collected_scans)} scans")
            print(f"Data length: {len(raw_data)}")
            
            # Adjust wavelength array if necessary to match data length
            if len(raw_data) != len(self.wavelengths):
                print(f"Adjusting wavelength array to match data: {len(raw_data)} points")
                self.wavelengths = np.linspace(self.wavelength_start, self.wavelength_end, len(raw_data))
            
            # Apply dark correction if available
            if self.dark_spectrum is not None and self.use_dark_correction:
                print("Applying dark correction...")
                # Ensure dark spectrum length matches data
                if len(self.dark_spectrum) == len(raw_data):
                    dark_corrected = raw_data - self.dark_spectrum
                    # Ensure no negative values after dark correction
                    dark_corrected = np.maximum(dark_corrected, 0)
                    raw_data = dark_corrected
                else:
                    print(f"Warning: Dark spectrum length mismatch. Expected {len(raw_data)}, got {len(self.dark_spectrum)}")
            
            # Store the processed raw data
            self.spectrum_data = raw_data
            
            # Apply boxcar smoothing to reduce noise (sliding window average)
            boxcar_width = 3  # Must be odd number: 3, 5, 7, etc.
            smoothed_data = np.copy(raw_data)
            half_width = boxcar_width // 2
            
            for i in range(half_width, len(raw_data) - half_width):
                smoothed_data[i] = np.mean(raw_data[i-half_width:i+half_width+1])
            
            # Calculate reflectance if reference spectrum is available
            if self.reference_spectrum is not None and self.use_reference_correction:
                print("Calculating reflectance...")
                if len(self.reference_spectrum) == len(smoothed_data):
                    # Calculate reflectance as I/I0 * 100%
                    reflectance = (smoothed_data / self.reference_spectrum) * 100
                    # Clip to reasonable range
                    reflectance = np.clip(reflectance, 0, 100)
                    plot_data = reflectance
                    y_label = "Reflectance (%)"
                    y_max = 100
                else:
                    print(f"Warning: Reference spectrum length mismatch. Expected {len(smoothed_data)}, got {len(self.reference_spectrum)}")
                    plot_data = smoothed_data
                    y_label = "Intensity (counts)"
                    y_max = None
            else:
                # Just use the smoothed counts
                plot_data = smoothed_data
                y_label = "Intensity (counts)"
                y_max = None
            
            try:
                # Clear the previous plot
                self.ax.clear()
                
                # Plot with proper formatting
                min_value = np.min(plot_data)
                max_value = np.max(plot_data)
                
                # Add buffer for better visualization
                buffer = (max_value - min_value) * 0.1
                y_min = max(0, min_value - buffer)
                if y_max is None:
                    y_max = max_value + buffer
                
                self.ax.plot(self.wavelengths, plot_data, 'b-', 
                             linewidth=1.5, 
                             label=f'Spectrum ({len(plot_data)} points)')
                
                # Set y-axis limits and label
                self.ax.set_ylim(y_min, y_max)
                self.ax.set_ylabel(y_label)
                
                # Add legend
                self.ax.legend(loc='upper right')
                
                # Reapply plot settings
                self._setup_plot()
                
                # Force redraw
                self.plot_widget.draw()
                
                print("Plot updated successfully")
            except Exception as e:
                print(f"Error plotting data: {e}")
                traceback.print_exc()
        else:
            print("Failed to acquire spectrum data")

    def collect_dark_spectrum(self, instance):
        """Collect a dark spectrum for noise correction."""
        # Ensure light source is off or sample port is blocked
        popup = Popup(title='Dark Spectrum Collection', 
                      content=Label(text='Ensure light source is OFF or\nsample port is completely blocked.\nThen click Continue.'),
                      size_hint=(0.6, 0.4))
        
        # Add buttons
        btn_layout = BoxLayout(size_hint=(1, 0.3), orientation='horizontal')
        cancel_btn = Button(text='Cancel')
        continue_btn = Button(text='Continue')
        
        cancel_btn.bind(on_release=popup.dismiss)
        continue_btn.bind(on_release=lambda x: self._perform_dark_collection(popup))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(continue_btn)
        
        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(Label(text='Ensure light source is OFF or\nsample port is completely blocked.\nThen click Continue.'))
        popup.content.add_widget(btn_layout)
        
        popup.open()

    def _perform_dark_collection(self, popup):
        """Actually collect the dark spectrum after user confirmation."""
        popup.dismiss()
        
        # Show progress indicator
        progress_popup = Popup(title='Collecting Dark Spectrum', 
                               content=Label(text='Please wait...'),
                               size_hint=(0.6, 0.3))
        progress_popup.open()
        
        # Collect multiple scans for better dark spectrum
        dark_scans = []
        DARK_SCANS = 20  # More scans for better dark noise profile
        
        for _ in range(DARK_SCANS):
            acquired = request_spectrum(
                self.spectrometer.usb_device,
                self.spectrometer.packet_size,
                self.spectrometer.spectra_ep_in,
                self.spectrometer.cmd_ep_out
            )
            if acquired:
                dark_scans.append(acquired)
        
        if dark_scans:
            # Average the dark scans
            self.dark_spectrum = np.mean(dark_scans, axis=0)
            print(f"Dark spectrum collected - avg value: {np.mean(self.dark_spectrum):.2f}")
            
            # Save dark spectrum for future use
            np.savetxt('dark_spectrum.csv', np.column_stack((self.wavelengths, self.dark_spectrum)), 
                       delimiter=',', header='Wavelength,Dark_Counts')
            
            progress_popup.dismiss()
            Popup(title='Success', 
                  content=Label(text='Dark spectrum collected successfully!'),
                  size_hint=(0.6, 0.3)).open()
        else:
            progress_popup.dismiss()
            Popup(title='Error', 
                  content=Label(text='Failed to collect dark spectrum.'),
                  size_hint=(0.6, 0.3)).open()

    def collect_reference_spectrum(self, instance):
        """Collect a white reference spectrum for reflectance calculation."""
        # Similar to dark spectrum collection but with white reference in place
        popup = Popup(title='Reference Spectrum Collection', 
                      content=Label(text='Place white reference standard at\nthe sample port and ensure light is ON.\nThen click Continue.'),
                      size_hint=(0.6, 0.4))
        
        # Add buttons
        btn_layout = BoxLayout(size_hint=(1, 0.3), orientation='horizontal')
        cancel_btn = Button(text='Cancel')
        continue_btn = Button(text='Continue')
        
        cancel_btn.bind(on_release=popup.dismiss)
        continue_btn.bind(on_release=lambda x: self._perform_reference_collection(popup))
        
        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(Label(text='Place white reference standard at\nthe sample port and ensure light is ON.\nThen click Continue.'))
        popup.content.add_widget(btn_layout)
        
        popup.open()

    def _perform_reference_collection(self, popup):
        """Actually collect the reference spectrum after user confirmation."""
        popup.dismiss()
        
        # Show progress indicator
        progress_popup = Popup(title='Collecting Reference Spectrum', 
                               content=Label(text='Please wait...'),
                               size_hint=(0.6, 0.3))
        progress_popup.open()
        
        # Collect multiple scans for better reference spectrum
        ref_scans = []
        REF_SCANS = 10
        
        for _ in range(REF_SCANS):
            acquired = request_spectrum(
                self.spectrometer.usb_device,
                self.spectrometer.packet_size,
                self.spectrometer.spectra_ep_in,
                self.spectrometer.cmd_ep_out
            )
            if acquired and self.dark_spectrum is not None:
                # Apply dark correction immediately
                corrected = np.array(acquired) - self.dark_spectrum
                corrected = np.maximum(corrected, 0)  # Ensure no negative values
                ref_scans.append(corrected)
            elif acquired:
                ref_scans.append(acquired)
        
        if ref_scans:
            # Average the reference scans
            self.reference_spectrum = np.mean(ref_scans, axis=0)
            print(f"Reference spectrum collected - avg value: {np.mean(self.reference_spectrum):.2f}")
            
            # Save reference spectrum for future use
            np.savetxt('reference_spectrum.csv', np.column_stack((self.wavelengths, self.reference_spectrum)), 
                       delimiter=',', header='Wavelength,Reference_Counts')
            
            # Enable reference correction
            self.use_reference_correction = True
            
            progress_popup.dismiss()
            Popup(title='Success', 
                  content=Label(text='Reference spectrum collected successfully!'),
                  size_hint=(0.6, 0.3)).open()
        else:
            progress_popup.dismiss()
            Popup(title='Error', 
                  content=Label(text='Failed to collect reference spectrum.'),
                  size_hint=(0.6, 0.3)).open()

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
            self.plot_widget.draw()
        except Exception as e:
            print(f"Error loading file: {e}")

    def scale_to_fill(self, instance):
        """Scale the plot to fill the window."""
        self.ax.autoscale()
        self._update_grid()
        self.plot_widget.draw()

    def zoom_in(self, instance):
        """Zoom into the plot."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] * 0.9, xlim[1] * 0.9)
        self.ax.set_ylim(ylim[0] * 0.9, ylim[1] * 0.9)
        self.plot_widget.draw()

    def zoom_out(self, instance):
        """Zoom out of the plot."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] * 1.1, xlim[1] * 1.1)
        self.ax.set_ylim(ylim[0] * 1.1, ylim[1] * 1.1)
        self.plot_widget.draw()

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
        self.plot_widget.draw()

    def copy_data(self, instance):
        """Copy the current spectrum data to clipboard."""
        if hasattr(self, 'spectrum_data') and self.spectrum_data is not None:
            try:
                import pyperclip  # You'll need to install this: pip install pyperclip
                
                # Create a formatted string with wavelength and intensity data
                data_str = "Wavelength (nm),Intensity\n"
                for i in range(len(self.wavelengths)):
                    data_str += f"{self.wavelengths[i]:.2f},{self.spectrum_data[i]:.2f}\n"
                
                # Copy to clipboard
                pyperclip.copy(data_str)
                
                # Notify user
                Popup(title='Success', 
                      content=Label(text='Spectrum data copied to clipboard'),
                      size_hint=(0.6, 0.3)).open()
            except Exception as e:
                print(f"Error copying to clipboard: {e}")
                Popup(title='Error', 
                      content=Label(text=f'Failed to copy: {str(e)}'),
                      size_hint=(0.6, 0.3)).open()
        else:
            Popup(title='Error', 
                  content=Label(text='No spectrum data available to copy'),
                  size_hint=(0.6, 0.3)).open()

    def save_as_csv(self, instance):
        """Save the current spectrum data to a CSV file."""
        if hasattr(self, 'spectrum_data') and self.spectrum_data is not None:
            # Open a file chooser popup
            file_chooser = FileChooserListView(filters=['*.csv'])
            
            # Create a save button
            save_button = Button(text='Save', size_hint=(1, 0.1))
            cancel_button = Button(text='Cancel', size_hint=(1, 0.1))
            
            # Create a layout for the buttons
            buttons = BoxLayout(size_hint=(1, 0.1), orientation='horizontal')
            buttons.add_widget(save_button)
            buttons.add_widget(cancel_button)
            
            # Create a layout for the file chooser and buttons
            content = BoxLayout(orientation='vertical')
            content.add_widget(file_chooser)
            content.add_widget(buttons)
            
            # Create the popup
            popup = Popup(title='Save Spectrum Data', content=content, size_hint=(0.9, 0.9))
            
            # Define save action
            def save_file(instance):
                if file_chooser.selection:
                    selected_dir = file_chooser.path
                    filename = file_chooser.selection[0] if file_chooser.selection[0].endswith('.csv') else file_chooser.selection[0] + '.csv'
                    
                    # Check if we're selecting a directory
                    if os.path.isdir(filename):
                        filename = os.path.join(filename, 'spectrum_data.csv')
                else:
                    # If no selection, use default path
                    selected_dir = file_chooser.path
                    filename = os.path.join(selected_dir, 'spectrum_data.csv')
                
                # Convert counts to reflectance for saving
                max_possible_count = 65535
                reflectance_data = np.array(self.spectrum_data) / max_possible_count * 100
                
                # Save data with metadata
                save_with_metadata(
                    self.wavelengths, 
                    reflectance_data,  # Save reflectance instead of raw counts
                    filename=filename,
                    metadata={
                        'Device': 'NIR-Quest',
                        'Integration time': '100ms',
                        'Units': 'Reflectance (%)',  # Note the units in metadata
                        'Raw count max': str(max(self.spectrum_data))  # Keep raw info too
                    }
                )
                popup.dismiss()
            
            # Define cancel action
            def cancel(instance):
                popup.dismiss()
            
            # Bind actions to buttons
            save_button.bind(on_press=save_file)
            cancel_button.bind(on_press=cancel)
            
            # Open the popup
            popup.open()

    def print_graph(self, instance):
        """Print the current graph."""
        try:
            # Save the figure to a temporary file and open the print dialog
            import tempfile
            import os
            import subprocess
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                temp_name = temp.name
            
            # Save the current figure
            self.fig.savefig(temp_name, dpi=300, bbox_inches='tight')
            
            # Open the file with the default viewer, which should have print capability
            if os.name == 'nt':  # Windows
                os.startfile(temp_name, 'print')
            elif os.name == 'posix':  # macOS or Linux
                if 'darwin' in os.sys.platform:  # macOS
                    subprocess.call(('open', temp_name))
                else:  # Linux
                    subprocess.call(('xdg-open', temp_name))
            
            print(f"Plot saved to {temp_name} and print dialog opened")
        except Exception as e:
            print(f"Error printing: {e}")
            Popup(title='Error', 
                  content=Label(text=f'Failed to print: {str(e)}'),
                  size_hint=(0.6, 0.3)).open()

    def set_integration_time(self, instance):
        """Open a dialog to set integration time."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Current integration time display
        current_time = 100  # Default ms, replace with actual value if available
        
        # Integration time slider
        slider_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        slider_label = Label(text="Integration Time (ms):", size_hint=(0.4, 1))
        time_slider = Slider(min=1, max=1000, value=current_time, size_hint=(0.6, 1))
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(time_slider)
        
        # Value display
        value_label = Label(text=f"{int(time_slider.value)} ms")
        
        # Update value display when slider moves
        def update_label(instance, value):
            value_label.text = f"{int(value)} ms"
        time_slider.bind(value=update_label)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        apply_btn = Button(text="Apply", size_hint=(0.5, 1))
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(apply_btn)
        
        # Build the layout
        content.add_widget(slider_layout)
        content.add_widget(value_label)
        content.add_widget(button_layout)
        
        # Create the popup
        popup = Popup(title='Set Integration Time', content=content, size_hint=(0.7, 0.4))
        
        # Button actions
        cancel_btn.bind(on_release=popup.dismiss)
        apply_btn.bind(on_release=lambda x: self._apply_integration_time(popup, time_slider.value))
        
        popup.open()

    def _apply_integration_time(self, popup, integration_time):
        """Apply the selected integration time to the spectrometer."""
        integration_time = int(integration_time)
        popup.dismiss()
        
        try:
            # Here you would call the appropriate USB command to set integration time
            # on the NIRQuest spectrometer. This requires proper USB command structure.
            # For example (pseudo-code):
            set_integration_time_command(
                self.spectrometer.usb_device,
                self.spectrometer.cmd_ep_out,
                integration_time
            )
            
            print(f"Integration time set to {integration_time} ms")
            
            # Show confirmation
            Popup(title='Success', 
                  content=Label(text=f'Integration time set to {integration_time} ms'),
                  size_hint=(0.6, 0.3)).open()
        except Exception as e:
            print(f"Error setting integration time: {e}")
            Popup(title='Error', 
                  content=Label(text=f'Failed to set integration time: {str(e)}'),
                  size_hint=(0.6, 0.3)).open()

    def set_averaging_options(self, instance):
        """Open a dialog to set signal averaging options."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Enable/disable averaging
        avg_enabled_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        avg_enabled_label = Label(text="Enable Averaging:", size_hint=(0.6, 1))
        avg_enabled_switch = Switch(active=self.averaging_enabled, size_hint=(0.4, 1))
        avg_enabled_layout.add_widget(avg_enabled_label)
        avg_enabled_layout.add_widget(avg_enabled_switch)
        
        # Number of scans to average
        scans_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        scans_label = Label(text="Scans to Average:", size_hint=(0.6, 1))
        scans_slider = Slider(min=1, max=50, value=self.scans_to_average, size_hint=(0.4, 1))
        scans_layout.add_widget(scans_label)
        scans_layout.add_widget(scans_slider)
        
        # Value display
        value_label = Label(text=f"{int(scans_slider.value)} scans")
        
        # Update value display when slider moves
        def update_label(instance, value):
            value_label.text = f"{int(value)} scans"
        scans_slider.bind(value=update_label)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        apply_btn = Button(text="Apply", size_hint=(0.5, 1))
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(apply_btn)
        
        # Build the layout
        content.add_widget(avg_enabled_layout)
        content.add_widget(scans_layout)
        content.add_widget(value_label)
        content.add_widget(button_layout)
        
        # Create the popup
        popup = Popup(title='Signal Averaging Settings', content=content, size_hint=(0.7, 0.5))
        
        # Button actions
        cancel_btn.bind(on_release=popup.dismiss)
        apply_btn.bind(on_release=lambda x: self._apply_averaging_settings(
            popup, avg_enabled_switch.active, int(scans_slider.value)))
        
        popup.open()

    def _apply_averaging_settings(self, popup, enabled, scans):
        """Apply the selected averaging settings."""
        popup.dismiss()
        
        self.averaging_enabled = enabled
        self.scans_to_average = scans
        
        print(f"Averaging settings updated: enabled={enabled}, scans={scans}")
        
        # Show confirmation
        status = "enabled" if enabled else "disabled"
        Popup(title='Success', 
              content=Label(text=f'Signal averaging {status}\nScans to average: {scans}'),
              size_hint=(0.6, 0.3)).open()

    def check_icon_paths(self):
        """Debug method to verify icon paths exist."""
        import os
        
        icon_paths = [
            'frontend/icons/app_icon.png',
            'frontend/icons/new_project.png',
            'frontend/icons/open.png',
            'frontend/icons/run_n_pause.png',
            'frontend/icons/dark_mode.png',
            'frontend/icons/reference.png',
            'frontend/icons/scale_to_fill_window.png',
            'frontend/icons/zoom_into_graph.png',
            'frontend/icons/zoom_out.png',
            'frontend/icons/panning.png',
            'frontend/icons/spectrum_overlay.png',
            'frontend/icons/delete.png',
            'frontend/icons/copy_data_to_clipboard.png',
            'frontend/icons/save_as_csv.png',
            'frontend/icons/print_graph.png',
        ]
        
        print("Checking icon paths:")
        for path in icon_paths:
            exists = os.path.exists(path)
            print(f"{path}: {'EXISTS' if exists else 'MISSING'}")
        
        # Also check the current working directory
        print(f"Current working directory: {os.getcwd()}")

    def _update_bar_bg(self, instance, value):
        """Update the background rectangle of an icon bar when it moves or resizes."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Very light gray
            # Update the rectangle position and size
            Rectangle(pos=instance.pos, size=instance.size)
        
        # Debug output to verify position updates
        print(f"Updated bar background: pos={instance.pos}, size={instance.size}")

class SpectrumApp(App):
    def build(self):
        # Simplify app initialization for now to ensure the main screen appears
        print("Starting NIR Spectrometer Software...")
        
        # Create and return the main layout directly
        return MainLayout()

    def on_stop(self):
        """Clean up resources when the app stops."""
        if hasattr(self.root, 'spectrometer'):
            drop_spectrometer(self.root.spectrometer.usb_device)

if __name__ == '__main__':
    SpectrumApp().run()

