"""
Script to extract custom Dock icons from com.apple.dock.plist
"""

import os
import plistlib
import struct
from io import BytesIO
from PIL import Image


def extract_icon_from_book_data(book_data):
    """
    Extract icon from the 'book' binary data in Dock plist.
    The 'book' format is an IconFamily structure.
    """
    if not book_data or len(book_data) < 8:
        return None

    # The book data starts with 'book' magic number
    # followed by icon family data
    try:
        # Skip the 'book' header (8 bytes: 'book' + length)
        # The actual icon data starts after
        stream = BytesIO(book_data)

        # Read header
        magic = stream.read(4)
        if magic != b"book":
            print(f"Warning: Expected 'book' magic, got {magic}")

        # Read length
        length = struct.unpack(">I", stream.read(4))[0]
        print(f"Book data length: {length}")

        # The rest is icon family data
        # Try to extract as ICNS
        icon_data = stream.read()

        # Check if it looks like ICNS
        if icon_data[:4] == b"icns":
            print("Found ICNS format")
            # It's already an ICNS file
            return icon_data

        # Otherwise, try to find ICNS within
        icns_start = icon_data.find(b"icns")
        if icns_start != -1:
            print(f"Found ICNS at offset {icns_start}")
            return icon_data[icns_start:]

        # Try PNG
        png_start = icon_data.find(b"\x89PNG")
        if png_start != -1:
            print(f"Found PNG at offset {png_start}")
            return icon_data[png_start:]

        print(f"Unknown format, first 20 bytes: {icon_data[:20].hex()}")
        return None

    except Exception as e:
        print(f"Error extracting icon: {e}")
        return None


def extract_dock_custom_icons():
    """Extract all custom icons from the Dock plist."""
    plist_path = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")

    if not os.path.exists(plist_path):
        print(f"Dock plist not found at {plist_path}")
        return

    with open(plist_path, "rb") as f:
        plist_data = plistlib.load(f)

    persistent_apps = plist_data.get("persistent-apps", [])

    print(f"Found {len(persistent_apps)} items in Dock\n")

    for idx, item in enumerate(persistent_apps):
        tile_data = item.get("tile-data", {})

        # Get app info
        bundle_id = tile_data.get("bundle-identifier", "unknown")
        file_label = tile_data.get("file-label", "unknown")

        print(f"[{idx}] {file_label} ({bundle_id})")

        # Check for custom icon in 'book' field
        book_data = tile_data.get("book")
        if book_data:
            print(f"  -> Has custom icon (book data: {len(book_data)} bytes)")

            # Extract the icon
            icon_data = extract_icon_from_book_data(book_data)

            if icon_data:
                # Save to file
                output_dir = os.path.expanduser("~/Desktop/dock_icons")
                os.makedirs(output_dir, exist_ok=True)

                # Determine file extension
                if icon_data[:4] == b"icns":
                    ext = "icns"
                elif icon_data[:4] == b"\x89PNG":
                    ext = "png"
                else:
                    ext = "bin"

                output_path = os.path.join(output_dir, f"{file_label}_icon.{ext}")
                with open(output_path, "wb") as f:
                    f.write(icon_data)
                print(f"  -> Saved to: {output_path}")

                # Try to convert ICNS to PNG for easy viewing
                if ext == "icns":
                    try:
                        img = Image.open(BytesIO(icon_data))
                        png_path = output_path.replace(".icns", ".png")
                        img.save(png_path, "PNG")
                        print(f"  -> Converted to PNG: {png_path}")
                    except Exception as e:
                        print(f"  -> Could not convert to PNG: {e}")
            else:
                print(f"  -> Failed to extract icon")
        else:
            print(f"  -> No custom icon")

        print()


if __name__ == "__main__":
    extract_dock_custom_icons()
