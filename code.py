import time, gc, os
import adafruit_dotstar
import board
import feathers2
import displayio
import adafruit_il0373
import terminalio
import busio
from adafruit_display_text import label
import ipaddress
import wifi
import socketpool
import ssl
import adafruit_requests

BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000

# Change text colors, choose from the following values:
# BLACK, RED, WHITE
FOREGROUND_COLOR = RED
BACKGROUND_COLOR = WHITE

DISPLAY_WIDTH = 296
DISPLAY_HEIGHT = 128


def setup_display():
    """
    Returns the display and display bus
    """
    # Define the pins needed for display use
    # This pinout is for a Feather M4 and may be different for other boards
    spi = busio.SPI(board.SCK, board.MOSI)
    display_bus=displayio.FourWire(
        spi, command=board.D6, chip_select=board.D5,
        baudrate=1000000)
    time.sleep(1)


    time.sleep(1)  # Wait a bit
    print("setup display_bus")
    # Create the display object - the third color is red (0xff0000)


    display=adafruit_il0373.IL0373(
        display_bus,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        rotation=270,
        black_bits_inverted=False,
        color_bits_inverted=False,
        grayscale=True,
        refresh_time=1)

    return( display_bus, display)

def display_text( display, x, y, text ):
    """
    Display the given text at point x, y on display
    """
# Create a display group for our screen objects
    g = displayio.Group(max_size=10)
    print("Setup display group")

    # Set a background
    background_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
    # Map colors in a palette
    palette = displayio.Palette(1)
    palette[0] = BACKGROUND_COLOR

    # Create a Tilegrid with the background and put in the displayio group
    t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
    g.append(t)

    # Draw simple text using the built-in font into a displayio group
    text_group = displayio.Group(max_size=10, scale=2, x=x, y=y)
    text_area = label.Label(terminalio.FONT, text=text, color=FOREGROUND_COLOR)
    text_group.append(text_area)  # Add this text to the text group
    g.append(text_group)

    # Place the display group on the screen
    display.show(g)


    # Refresh the display to have everything show on the display
    # NOTE: Do not refresh eInk displays more often than 180 seconds!
    display.refresh()

    time.sleep(180)


print("Tide Clock ")


# Used to ensure the display is free in CircuitPython
displayio.release_displays()

display_bus, display = setup_display()

#display_text( display, 5,10, "Tide Clock")

for network in wifi.radio.start_scanning_networks():
    print(network, network.ssid, network.channel)
wifi.radio.stop_scanning_networks()

print('Done')

while True:
    pass


