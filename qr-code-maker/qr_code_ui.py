import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
import io
import re
from datetime import datetime
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import os
import subprocess
import sys

def hex_to_rgb(hex_color):
    """Convert a hex color string (e.g., #RRGGBB) to an (R, G, B) tuple."""
    print(f"Converting hex color: {hex_color}")  # Log the input hex color
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb
    elif len(hex_color) == 3:  # Handle shorthand hex colors like #RGB
        rgb = tuple(int(hex_color[i]*2, 16) for i in range(3))
        return rgb
    raise ValueError("Invalid hex color format. Use #RRGGBB or #RGB.")

def generate_qr_code(url, color, size):
    error_correction_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
    qr = qrcode.QRCode(
        version=int(version_var.get()),
        error_correction=error_correction_map[error_correction_var.get()],
        box_size=size,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Use the selected color from the color preview
    fill_color_in = color_preview.color_code

    img = qr.make_image(fill_color=fill_color_in, back_color=(255, 255, 255))  # White background
    return img

def generate_filename():
    url = url_entry.get("1.0", "end-1c")  # Get the URL from the text box
    sanitized_url = re.sub(r'[^a-zA-Z0-9]', '_', url)  # Replace non-alphanumeric characters with underscores
    datestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{sanitized_url}_{datestamp}"

def save_qr_code_as_png(image):
    default_filename = generate_filename() + ".png"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=default_filename,
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if file_path:
        image.save(file_path)
        messagebox.showinfo("Success", f"QR code saved as PNG to {file_path}")

        # Offer a file explorer link to the saved file
        if os.name == 'nt':  # Windows
            os.startfile(os.path.dirname(file_path))
        elif os.name == 'posix':  # macOS/Linux
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", os.path.dirname(file_path)])

def save_qr_code_as_svg():
    default_filename = generate_filename() + ".svg"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".svg",
        initialfile=default_filename,
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )
    if file_path:
        try:
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgImage
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=int(size_var.get()),
                border=4,
            )
            qr.add_data(url_entry.get("1.0", "end-1c"))  # Get the URL from the text box
            qr.make(fit=True)
            img = qr.make_image(image_factory=factory)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(img.to_string())  # Ensure the SVG content is written as a string
            messagebox.showinfo("Success", f"QR code saved as SVG to {file_path}")
        except ImportError:
            messagebox.showerror("Error", "SVG support requires the qrcode[svg] package.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def update_preview():
    url = url_entry.get("1.0", "end-1c")  # Get the URL from the text box
    color = color_preview.color_code  # Use the selected color from the preview
    try:
        size = int(size_var.get())  # Use the selected value from the dropdown
        img = generate_qr_code(url, color, size)
        img.thumbnail((300, 300))  # Ensure the preview image is resized to exactly 300x300 pixels
        img_tk = ImageTk.PhotoImage(img)
        preview_label.config(image=img_tk)
        preview_label.image = img_tk
        preview_label.qr_image = img  # Store the original image for saving

        preview_label.config(width=300, height=300)  # Set the preview window to 300x300 pixels

        print(f"Generated QR code size: {img.size[0]}x{img.size[1]} pixels")  # Log the size of the QR code
        print(f"Foreground color used: {color}")  # Log the color used for debugging
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Replace the color text field with a color preview and palette selection
def choose_color():
    color_code = colorchooser.askcolor(title="Choose QR Code Color")[1]
    if color_code:
        color_preview.config(bg=color_code)  # Update the color preview
        color_preview.color_code = color_code  # Store the selected color
    else:
        # Set a valid default color if no color is chosen
        color_preview.config(bg="#000000")
        color_preview.color_code = "#000000"  # Default to black

# Create the main application window
root = tk.Tk()
root.title("QR Code Generator")

# Create a frame for the left column (generation elements)
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Create a frame for the right column (preview and save buttons)
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# Move generation elements to the left frame
url_label = tk.Label(left_frame, text="Enter URL (max 256 characters):")
url_label.pack()
url_entry = tk.Text(left_frame, width=40, height=2, wrap="word")  # Double-line text box
url_entry.pack()
url_entry.insert("1.0", "https://www.royalmanortheatre.co.uk")

# Function to enforce the character limit
def enforce_url_limit(event):
    content = url_entry.get("1.0", "end-1c")  # Get the content of the text box
    if len(content) > 256:
        url_entry.delete("1.0", "end")
        url_entry.insert("1.0", content[:256])  # Truncate to 256 characters

# Bind the character limit enforcement to the text box
url_entry.bind("<KeyRelease>", enforce_url_limit)

# Replace the color text field with a color preview and palette selection
color_label = tk.Label(left_frame, text="QR Code Color:")
color_label.pack()
color_preview = tk.Label(left_frame, bg="black", width=20, height=2, relief="sunken")
color_preview.pack()
color_preview.color_code = "#000000"  # Default color

color_button = tk.Button(left_frame, text="Choose Color", command=choose_color)
color_button.pack()

size_label = tk.Label(left_frame, text="Select QR Code Size:")
size_label.pack()
size_var = tk.StringVar(value="5")  # Default size
size_dropdown = ttk.Combobox(left_frame, textvariable=size_var, state="readonly")
size_dropdown['values'] = [str(i) for i in range(1, 11)]
size_dropdown.pack()

# Add a dropdown for error correction levels
error_correction_label = tk.Label(left_frame, text="Select Error Correction Level:")
error_correction_label.pack()
error_correction_var = tk.StringVar(value="L")  # Default error correction level
error_correction_dropdown = ttk.Combobox(left_frame, textvariable=error_correction_var, state="readonly")
error_correction_dropdown['values'] = ["L", "M", "Q", "H"]
error_correction_dropdown.pack()

# Add a dropdown for QR code version
version_label = tk.Label(left_frame, text="Select QR Code Version:")
version_label.pack()
version_var = tk.StringVar(value="1")  # Default version
version_dropdown = ttk.Combobox(left_frame, textvariable=version_var, state="readonly")
version_dropdown['values'] = [str(i) for i in range(1, 41)]  # Versions 1 to 40
version_dropdown.pack()

# Add a dropdown for image factory options
image_factory_label = tk.Label(left_frame, text="Select Image Factory:")
image_factory_label.pack()
image_factory_var = tk.StringVar(value="Default")  # Default image factory
image_factory_dropdown = ttk.Combobox(left_frame, textvariable=image_factory_var, state="readonly")
image_factory_dropdown['values'] = ["Default", "StyledPilImage"]
image_factory_dropdown.pack()

generate_button = tk.Button(left_frame, text="Generate QR Code", command=update_preview)
generate_button.pack()

# Move preview and save buttons to the right frame
preview_label = tk.Label(right_frame, text="QR Code Preview", bg="white", width=25, height=12)
preview_label.pack(pady=10)

png_button = tk.Button(right_frame, text="Download as PNG", command=lambda: save_qr_code_as_png(preview_label.qr_image))
png_button.pack()

svg_button = tk.Button(right_frame, text="Download as SVG", command=save_qr_code_as_svg)
svg_button.pack()

# Run the application
root.mainloop()