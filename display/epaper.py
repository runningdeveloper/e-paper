"""
Waveshare E-Paper Display Module

This module provides functions to control the Waveshare e-paper display.
"""
import platform
import os
import time
from PIL import Image, ImageDraw, ImageFont
import os.path

# Check if we're running on a Raspberry Pi
def is_raspberry_pi():
    """
    Check if the current system is a Raspberry Pi
    
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise
    """
    # Check for Raspberry Pi model in /proc/device-tree/model
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return 'raspberry pi' in model.lower()
    except (FileNotFoundError, IOError, OSError) as e:
        # Handle the case where the file doesn't exist or can't be read
        pass
    
    # Alternative check for arm processor and specific hardware
    return platform.machine().startswith('arm') and os.path.exists('/dev/gpiomem')

# Import the e-paper library only if we're on a Raspberry Pi
if is_raspberry_pi():
    try:
        from lib.waveshare_epd import epd2in13
        print("Running on Raspberry Pi with e-paper support")
        PI_AVAILABLE = True
    except ImportError:
        print("Failed to import e-paper library")
        PI_AVAILABLE = False
else:
    print("Not running on Raspberry Pi - e-paper display functionality will be simulated")
    PI_AVAILABLE = False

def init_and_clear_display():
    """
    Initialize and clear the e-paper display
    Returns the initialized EPD object
    """
    if PI_AVAILABLE:
        epd = epd2in13.EPD()
        print("Initializing and clearing display")
        epd.init(epd.lut_full_update)
        epd.Clear(0xFF)
        time.sleep(2)
        return epd
    else:
        print("Simulating display initialization and clearing")
        return None

def display_image(image_path):
    """
    Display an image on the e-paper display
    
    Args:
        image_path (str): Path to the BMP image file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if PI_AVAILABLE:
            epd = init_and_clear_display()
            print(f"Displaying image: {image_path}")
            
            image = Image.open(image_path)
            epd.display(epd.getbuffer(image))
            time.sleep(2)
            
            # Put the display to sleep to save power
            epd.sleep()
        else:
            # Mock implementation for development
            print(f"[MOCK] Would display image: {image_path}")
            # Still open the image to check if it exists and is valid
            image = Image.open(image_path)
            print(f"[MOCK] Image size: {image.size}, mode: {image.mode}")
        
        return True
    except Exception as e:
        print(f"Error with image: {e}")
        return False

def display_text(text, max_width=122, max_height=250, rotate=True):
    """
    Display text on the e-paper display with dynamically sized font
    
    Args:
        text (str): Text to display on the screen
        max_width (int): Maximum width of the display in pixels (default: 122)
        max_height (int): Maximum height of the display in pixels (default: 250)
        rotate (bool): Whether to rotate the text by 90 degrees (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the absolute path to the font file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, 'Ranchers-Regular.ttf')
        
        # If we're rotating, swap width and height for initial text placement
        if rotate:
            # Swap dimensions for rotated text
            layout_width, layout_height = max_height, max_width
        else:
            layout_width, layout_height = max_width, max_height
            
        # Create a blank white image for the text
        image = Image.new('1', (layout_width, layout_height), 255)  # '1' mode is 1-bit pixels, black and white
        draw = ImageDraw.Draw(image)
        
        # Start with a reasonable font size
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)
        
        # Calculate text size and adjust font size to fit
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        
        # Dynamically adjust font size to fit within display
        while (text_width > layout_width - 10 or text_height > layout_height - 10) and font_size > 8:
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        
        # Calculate position to center the text
        x = (layout_width - text_width) // 2
        y = (layout_height - text_height) // 2
        
        # Draw the text on the image
        draw.text((x, y), text, font=font, fill=0)
        
        # Rotate the image if needed
        if rotate:
            # Rotate 90 degrees counterclockwise
            image = image.rotate(270, expand=True)
        
        if PI_AVAILABLE:
            epd = init_and_clear_display()
            print(f"Displaying text: {text}")
            epd.display(epd.getbuffer(image))
            time.sleep(2)
            
            # Put the display to sleep to save power
            epd.sleep()
        else:
            # Mock implementation for development
            print(f"[MOCK] Would display text: {text}")
            print(f"[MOCK] Text size: {text_width}x{text_height}, Font size: {font_size}")
            # Save the mock image to a file for debugging
            debug_path = os.path.join(current_dir, '../bmps/text_preview.bmp')
            image.save(debug_path)
            print(f"[MOCK] Text preview saved to: {debug_path}")
        
        return True
    except Exception as e:
        print(f"Error displaying text: {e}")
        return False

