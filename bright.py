#! /usr/bin/env python3
import re
import tkinter as tk
from tkinter import ttk
import subprocess


class BrightnessControllerApp:
    def __init__(self):
        # Set up the main window
        self.root = tk.Tk()
        self.root.title("Brightness Controller")
        self.root.resizable(False, False)

        # Set default font
        default_font = ("Helvetica", 11)
        self.style = ttk.Style()
        self.style.configure("TLabel", font=default_font)
        self.style.configure("TFrame", padding=10)
        self.style.configure("TScale", troughcolor='gray', sliderthickness=15)

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
        subprocess.run(["ddcutil", "--bus", bus, "setvcp", "10", str(int(float(value)))])
        # Update the label if necessary (optional)

    def on_slider_release(self, event, bus):
        """Callback when the slider is released."""
        slider = event.widget
        value = slider.get()
        self.update_brightness(bus, value)

    def create_gui(self):
        """Creates the GUI with sliders for each detected display."""
        for display in self.displays:
            frame = ttk.Frame(self.root, padding=(10, 5))
            frame.pack(fill="x")

            # Display label with name and bus number
            label = ttk.Label(frame, text=f"{display['name']} (Bus {display['bus']})", font=("Helvetica", 12, "bold"))
            label.pack(side="top", anchor="w")

            # Slider to control brightness
            bus = display["bus"]
            max_brightness = display["max_brightness"]
            brightness = display["brightness"]

            slider = tk.Scale(
                frame,
                from_=0,
                to=max_brightness,
                orient="horizontal",
                length=300,
                showvalue=True,
                font=("Helvetica", 10),
                troughcolor="#cccccc",
                command=None,  # We will bind to release event instead
            )
            slider.set(brightness)
            slider.pack(fill="x", padx=5, pady=5)

            # Bind the slider release event
            slider.bind("<ButtonRelease-1>", lambda event, b=bus: self.on_slider_release(event, b))

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
