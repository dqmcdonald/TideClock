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
import json
from adafruit_datetime import datetime, date, timezone, timedelta
import secrets

BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000

# Change text colors, choose from the following values:
# BLACK, RED, WHITE
FOREGROUND_COLOR = RED
BACKGROUND_COLOR = WHITE

DISPLAY_WIDTH = 296
DISPLAY_HEIGHT = 128


# Lyttleton Data:
LATITUDE = -43.611
LONGTITUDE = 172.717
NIWA_URL = "https://api.niwa.co.nz/tides/data"



def setup_display():
    """
    Returns the display, display bus and display group
    """
    # Define the pins needed for display use
    # This pinout is for a Feather M4 and may be different for other boards
    spi = busio.SPI(board.SCK, board.MOSI)
    display_bus=displayio.FourWire(
        spi, command=board.D6, chip_select=board.D5,
        baudrate=1000000)

    time.sleep(1)  # Wait a bit


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


    # Create a display group for our screen objects
    g = displayio.Group(max_size=10)

    # Set a background
    background_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
    # Map colors in a palette
    palette = displayio.Palette(1)
    palette[0] = BACKGROUND_COLOR

    # Create a Tilegrid with the background and put in the displayio group
    t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
    g.append(t)

    return(display_bus, display, g)

def display_text(display,group, x, y, text):
    """
    Display the given text at point x, y on display
    """


    # Draw simple text using the built-in font into a displayio group
    text_group = displayio.Group(max_size=10, scale=2, x=x, y=y)
    text_area = label.Label(terminalio.FONT, text=text, color=FOREGROUND_COLOR)
    text_group.append(text_area)  # Add this text to the text group
    group.append(text_group)


def update_display(display, group ):
    # Place the display group on the screen
    display.show(group)
    # Refresh the display to have everything show on the display
    # NOTE: Do not refresh eInk displays more often than 180 seconds!
    display.refresh()
    time.sleep(180)


def connect_to_ssid(ssid, password):
    """
    Given an SSID and password connect to that Wifi service
    """

    try:
        wifi.radio.connect(ssid=ssid,password=password)
    except ConnectionError:
        print("Connection to {} failed".format(ssid))
        raise


def get_tide_data(URL, apikey, lat, long):
    """
    Fetch tide data for Lyttleton from NIWA
    """

    pool = socketpool.SocketPool(wifi.radio)
    request = adafruit_requests.Session(pool, ssl.create_default_context())


    url = "{}?apikey={}&lat={}&long={}".format(URL, api_key, lat, long)

    print("Fetching data with {}".format(url))
    response = request.get(url)
    print("Response code:",response.status_code)
    return response.json()

####### Main Routine ##################

print("Tide Clock ")


(ssid,password, api_key) = (secrets.secrets["ssid"], secrets.secrets["password"], secrets.secrets["api_key"])
print("Connecting to '{}' with password '{}'".format(ssid, password))

connect_to_ssid(ssid, password)

print("Connection to {} complete".format( ssid ))
print("my IP addr:", wifi.radio.ipv4_address)

tide_data = get_tide_data(NIWA_URL, api_key, LATITUDE, LONGTITUDE)

vals = tide_data["values"]
print(vals)
first_time = vals[1]["time"]
first_time = first_time.replace('T', '*')
first_time = first_time.replace('Z','')
print(first_time)


first_datetime = datetime.fromisoformat(first_time)
UTC_offset = timedelta(hours=12)


print( first_datetime.ctime())

ft = first_datetime + UTC_offset
print(ft.ctime(), vals[1]["value"])


displayio.release_displays()

display_bus, display, group = setup_display()



#display_text( display, group, 5,10, "Tide Clock - Lyttleton")
#display_text( display, group, 5,30, "Date")
#update_display( display, group )


print('Done')

while True:
    pass


