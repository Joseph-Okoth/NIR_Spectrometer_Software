from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import io
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class MatplotlibWidget(Widget):
    """Simple widget to embed matplotlib figures in Kivy"""
    figure = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(MatplotlibWidget, self).__init__(**kwargs)
        self.bind(size=self._update_figure)
        self.bind(pos=self._update_figure)
        if self.figure is None:
            self.figure = plt.figure()
        
    def _update_figure(self, *args):
        if not self.canvas or not self.figure:
            return
            
        # Draw matplotlib figure to buffer
        canvas = FigureCanvasAgg(self.figure)
        canvas.draw()
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        
        # Update Kivy canvas
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            tex = CoreImage(buf, ext='png').texture
            Rectangle(texture=tex, pos=self.pos, size=self.size)
    
    def draw(self):
        """Refresh the matplotlib figure"""
        Clock.schedule_once(lambda dt: self._update_figure(), 0)

def plot_spectrum(wavelengths, intensities):
    plt.plot(wavelengths, intensities)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (counts)")
    plt.title("Spectrum Window")
    plt.show()