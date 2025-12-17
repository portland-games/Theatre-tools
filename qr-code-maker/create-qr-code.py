#!/usr/bin/env python3
import qrcode
import argparse
from PIL import ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

def generate_qr_code(url, color, size, style, version, error_correction):
    error_correction_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction_map[error_correction],
        box_size=size,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Select the module drawer based on the style
    if style == "GappedSquare":
        module_drawer = GappedSquareModuleDrawer()
    elif style == "Circle":
        module_drawer = CircleModuleDrawer()
    else:
        module_drawer = SquareModuleDrawer()

    img = qr.make_image(image_factory=StyledPilImage, module_drawer=module_drawer, embeded_color=True, fill_color=color)  # Removed back_color parameter
    return img

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code with customizable options.")
    parser.add_argument("--url", required=True, help="The URL or data for the QR code.")
    parser.add_argument("--color", default="black", help="The color of the QR code (e.g., black, blue, #RRGGBB).")
    parser.add_argument("--size", type=int, default=10, help="The size of the QR code (e.g., 10).")
    parser.add_argument("--style", choices=["Square", "GappedSquare", "Circle"], default="Square", help="The style of the QR code modules.")
    parser.add_argument("--version", type=int, choices=range(1, 41), default=1, help="The version of the QR code (1 to 40).")
    parser.add_argument("--error_correction", choices=["L", "M", "Q", "H"], default="L", help="The error correction level (L, M, Q, H).")
    parser.add_argument("--output", default="qr_code.png", help="The output file name (e.g., qr_code.png).")

    args = parser.parse_args()

    try:
        # Validate color
        ImageColor.getrgb(args.color)
        qr_code = generate_qr_code(
            url=args.url,
            color=args.color,
            size=args.size,
            style=args.style,
            version=args.version,
            error_correction=args.error_correction,
        )
        qr_code.save(args.output)
        print(f"QR code generated and saved as '{args.output}'.")
    except ValueError as e:
        print(f"Error: {e}. Please enter valid inputs.")

if __name__ == "__main__":
    main()