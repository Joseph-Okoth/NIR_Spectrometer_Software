from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

class IconButton(Button):
    """Button with icon image and tooltip."""
    
    def __init__(self, icon_source="", tooltip_text="", **kwargs):
        # Set transparent background before init
        kwargs['background_color'] = (1, 1, 1, 1)  # White background for visibility
        super(IconButton, self).__init__(**kwargs)
        
        self.tooltip_text = tooltip_text
        self.tooltip = None
        
        # Create a clearer button style
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        # Update rectangle position when the button moves
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Set up vertical box layout
        layout = BoxLayout(orientation='vertical', padding=[2, 2, 2, 2])
        
        # Create image widget for the icon with better sizing
        try:
            self.icon = Image(
                source=icon_source,
                size_hint=(None, None),
                size=(36, 36),  # Slightly smaller fixed size for icon
                allow_stretch=True,
                keep_ratio=True
            )
            
            # Better centering with padding
            icon_container = BoxLayout(size_hint=(1, 0.8), padding=[4, 4, 4, 0])
            icon_container.add_widget(Widget(size_hint=(0.5, 1)))  # Spacer
            icon_container.add_widget(self.icon)
            icon_container.add_widget(Widget(size_hint=(0.5, 1)))  # Spacer
            
            layout.add_widget(icon_container)
            print(f"Successfully loaded icon: {icon_source}")
        except Exception as e:
            print(f"Error loading icon {icon_source}: {e}")
            # Add a placeholder if icon fails to load
            layout.add_widget(Label(text="Icon", size_hint=(1, 0.8)))
        
        # Add label below icon
        self.label = Label(
            text="",
            size_hint=(1, 0.2),
            font_size='10sp',
            color=(0, 0, 0, 1)  # Black text for better visibility
        )
        layout.add_widget(self.label)
        
        # Add layout to button
        self.add_widget(layout)
        
        # Bind mouse hover events for tooltip
        self.bind(on_enter=self.show_tooltip)
        self.bind(on_leave=self.hide_tooltip)
    
    def _update_rect(self, *args):
        """Update the rectangle position and size when button changes."""
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def show_tooltip(self, instance):
        """Show tooltip when mouse hovers over the button."""
        if not self.tooltip and self.tooltip_text:
            # Create tooltip as a small popup below the cursor
            self.tooltip = Popup(
                title='',
                content=Label(
                    text=self.tooltip_text,
                    color=(1, 1, 1, 1),  # White text
                    font_size='14sp'  # Slightly larger font
                ),
                size_hint=(None, None),
                size=(max(180, len(self.tooltip_text) * 6), 36),  # Slightly smaller size
                background_color=(0.3, 0.3, 0.3, 0.85),  # Slightly lighter background
                border=(0, 0, 0, 0)
            )
            
            # Position tooltip directly below the icon (not the cursor)
            pos = self.to_window(*self.pos)
            center_x = pos[0] + self.width / 2
            bottom_y = pos[1]
            
            # Place tooltip below the button
            self.tooltip.pos = (center_x - self.tooltip.width/2, bottom_y - self.tooltip.height - 5)
            
            self.tooltip.open()
    
    def hide_tooltip(self, instance):
        """Hide tooltip when mouse leaves the button."""
        if self.tooltip:
            self.tooltip.dismiss()
            self.tooltip = None
    
    def set_label_text(self, text):
        """Set the small label text below the icon."""
        self.label.text = text
