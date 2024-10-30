#! /usr/bin/env python3
import re
import tkinter as tk
from tkinter import ttk
import subprocess
import os


class BrightnessControllerApp:
    def __init__(self):
        # Set up the main window
        self.root = tk.Tk()
        self.root.title("Brightness Controller")
        self.root.resizable(False, False)
        self.root.configure(bg='#2E3440')  # Set a background color

        # Set default font and styles
        default_font = ("Helvetica", 11)
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        self.style.configure("TLabel", font=default_font, background='#2E3440', foreground='#D8DEE9')
        self.style.configure("TFrame", background='#2E3440')
        self.style.configure("TCheckbutton", background='#2E3440', foreground='#D8DEE9', font=default_font)
        self.style.map("TCheckbutton", background=[('active', '#3B4252')])

        # Variable to track checkbox state
        self.round_to_5_var = tk.BooleanVar(value=True)  # Checkbox checked by default
        self.round_to_5_var.trace_add('write', self.on_round_checkbox_toggle)

        # List to hold display controls for dynamic updates
        self.display_controls = []

        # Detect connected displays and initialize GUI
        self.displays = self.detect_displays()
        if self.displays:
            self.create_gui()
        else:
            self.show_error("No compatible displays detected.")

    def detect_displays(self):
        """
        Detects connected displays using ddcutil and returns a list of dictionaries
        containing display information: name, bus number, current brightness, and max brightness.
        """
        output = subprocess.run(["ddcutil", "detect"], capture_output=True, text=True).stdout
        displays = []

        # Split the output into blocks for each display
        for block in output.strip().split("\n\n"):
            if block and not block.startswith("Invalid display"):
                lines = block.strip().split("\n")
                # Extract display name and bus number
                try:
                    display_info = {
                        "name": lines[0].strip(),
                        "bus": lines[1].split("/dev/i2c-")[1].strip(),
                    }
                except IndexError:
                    continue  # Skip if parsing fails
                # Get current and max brightness
                brightness_output = subprocess.run(
                    ["ddcutil", "--bus", display_info["bus"], "getvcp", "10"],
                    capture_output=True,
                    text=True,
                ).stdout
                search = re.search(r"current value =\s*(\d+), max value =\s*(\d+)", brightness_output)
                if search:
                    display_info.update(
                        {
                            "brightness": int(search.group(1)),
                            "max_brightness": int(search.group(2)),
                        }
                    )
                else:
                    # Default values if brightness info is not available
                    display_info.update({"brightness": 50, "max_brightness": 100})
                displays.append(display_info)
        return displays

    def update_brightness(self, bus, value):
        """Sets the brightness of the specified bus (display) to the given value using ddcutil."""
        value = float(value)
        value = int(value)
        subprocess.run(["ddcutil", "--bus", bus, "setvcp", "10", str(value)])

    def on_slider_release(self, event, bus):
        """Callback when the slider is released."""
        slider = event.widget
        value = slider.get()
        self.update_brightness(bus, value)

    def on_round_checkbox_toggle(self, *args):
        """Callback when the round to 5 checkbox is toggled."""
        resolution = 5 if self.round_to_5_var.get() else 1
        for control in self.display_controls:
            # Get the current brightness before destroying the slider
            current_brightness = control['slider'].get()
            # Adjust brightness to nearest multiple of resolution
            if self.round_to_5_var.get():
                current_brightness = round(current_brightness / 5) * 5
            # Destroy the old slider
            control['slider'].destroy()
            # Create a new slider with updated resolution
            slider = self.create_slider(
                parent=control['frame'],
                bus=control['bus'],
                max_brightness=control['max_brightness'],
                brightness=current_brightness,  # Use the adjusted brightness
                resolution=resolution
            )
            control['slider'] = slider  # Update the reference

    def create_slider(self, parent, bus, max_brightness, brightness, resolution):
        """Creates a slider widget."""
        slider = tk.Scale(
            parent,
            from_=0,
            to=max_brightness,
            orient="horizontal",
            length=300,
            showvalue=True,
            font=("Helvetica", 10),
            troughcolor="#4C566A",
            bg='#2E3440',
            fg='#D8DEE9',
            highlightthickness=0,
            resolution=resolution,
            command=None,  # We will bind to release event instead
        )
        slider.set(brightness)
        slider.pack(fill="x", padx=5, pady=5)
        # Bind the slider release event
        slider.bind("<ButtonRelease-1>", lambda event, b=bus: self.on_slider_release(event, b))
        return slider

    def create_gui(self):
        """Creates the GUI with sliders for each detected display."""
        # Create a title label
        title_label = ttk.Label(self.root, text="Brightness Controller", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(10, 5))

        # Checkbox to round values to nearest 5
        checkbox_frame = ttk.Frame(self.root)
        checkbox_frame.pack(fill="x", padx=10)
        self.round_checkbox = ttk.Checkbutton(
            checkbox_frame,
            text="Round values to nearest 5",
            variable=self.round_to_5_var,
            onvalue=True,
            offvalue=False
        )
        self.round_checkbox.pack(side="left", anchor="w", pady=5)

        resolution = 5 if self.round_to_5_var.get() else 1

        for display in self.displays:
            frame = ttk.Frame(self.root, padding=(10, 5))
            frame.pack(fill="x", padx=10, pady=5)

            # Decorative separator
            separator = ttk.Separator(frame, orient='horizontal')
            separator.pack(fill='x', pady=5)

            # Display label with name and bus number
            label = ttk.Label(frame, text=f"{display['name']} (Bus {display['bus']})", font=("Helvetica", 12, "bold"))
            label.pack(side="top", anchor="w", pady=(5, 0))

            # Slider to control brightness
            bus = display["bus"]
            max_brightness = display["max_brightness"]
            brightness = display["brightness"]

            slider = self.create_slider(
                parent=frame,
                bus=bus,
                max_brightness=max_brightness,
                brightness=brightness,
                resolution=resolution
            )

            # Store references for dynamic updates
            self.display_controls.append({
                'frame': frame,
                'slider': slider,
                'bus': bus,
                'max_brightness': max_brightness
            })

    def show_error(self, message):
        """Displays an error message in the GUI if detection fails."""
        label = ttk.Label(self.root, text=message, foreground="red", font=("Helvetica", 12))
        label.pack(padx=20, pady=20)

    def run(self):
        """Starts the main application loop."""
        self.root.mainloop()


# Run the application
if __name__ == "__main__":
    app = BrightnessControllerApp()
    app.run()
