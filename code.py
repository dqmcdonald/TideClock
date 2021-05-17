import time, gc, os
import alarm
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

LINE_INCREMENT = 20 # Pixels for line spacing
LINE_START = 5  # X-offset for line display
TIDE_LINE_OFFSET = 20  # Tide lines are offset
DATE_OFFSET = 170 # Position for date line


SLEEP_TIME = 24*60*60 # Sleep for a day

# Lyttleton Data:
LATITUDE = -43.611
LONGTITUDE = 172.717
NIWA_URL = "https://api.niwa.co.nz/tides/data"
TIMEZONE_DB_URL = "http://api.timezonedb.com/v2.1/get-time-zone"


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

def display_text(display,group, x, y, text, scale=2):
    """
    Display the given text at point x, y on display
    """


    # Draw simple text using the built-in font into a displayio group
    text_group = displayio.Group(max_size=10, scale=int(scale), x=x, y=y)
    text_area = label.Label(terminalio.FONT, text=text, color=FOREGROUND_COLOR)
    text_group.append(text_area)  # Add this text to the text group
    group.append(text_group)


def update_display(display, group ):
    # Place the display group on the screen
    display.show(group)
    # Refresh the display to have everything show on the display
    # NOTE: Do not refresh eInk displays more often than 180 seconds!
    display.refresh()



def connect_to_ssid(ssid, password):
    """
    Given an SSID and password connect to that Wifi service
    """

    try:
        wifi.radio.connect(ssid=ssid,password=password)
    except ConnectionError:
        print("Connection to {} failed".format(ssid))
        raise


def get_tide_data(URL, api_key, lat, long):
    """
    Fetch tide data for Lyttleton from NIWA
    """

    pool = socketpool.SocketPool(wifi.radio)
    request = adafruit_requests.Session(pool, ssl.create_default_context())


    url = "{}?apikey={}&lat={}&long={}&numberOfDays=1".format(URL, api_key, lat, long)

    print("Fetching data with {}".format(url))
    response = request.get(url)
    print("Response code:",response.status_code)
    return response.json()

def get_utc_offset( URL, api_key ):
    """
    Use the timezone DB API to get the utc offset for our timezone

    Returns the offset in hours:
    """
    pool = socketpool.SocketPool(wifi.radio)
    request = adafruit_requests.Session(pool, ssl.create_default_context())


    url = "{}?key={}&format=json&fields=gmtOffset&by=zone&zone=Pacific/Auckland".format(URL, api_key)

    print("Fetching data with {}".format(url))
    response = request.get(url)
    print("Response code:",response.status_code)
    js=response.json()

    return js['gmtOffset']/3600

def convert_to_local_time( time_str, utc_offset ):
    """
    Convert the UTC tide time string to a local time datetime object based on the UTC offset
    """
    tide_time = time_str
    tide_time = tide_time.replace('T', '*')
    tide_time = tide_time.replace('Z','')

    tide_dt_utc = datetime.fromisoformat(tide_time)
    UTC_offset = timedelta(hours=utc_offset)
    tide_dt_local = tide_dt_utc + UTC_offset
    return tide_dt_local


####### Main Routine ##################

print("Tide Clock ")


(ssid,password, niwa_api_key, timezone_db_api_key) = (secrets.secrets["ssid"], secrets.secrets["password"],
    secrets.secrets["niwa_api_key"], secrets.secrets["timezone_db_api_key"])
print("Connecting to '{}' with password '{}'".format(ssid, password))

connect_to_ssid(ssid, password)
print("Connection to {} complete".format( ssid ))
print("my IP addr:", wifi.radio.ipv4_address)

# Fetch Tide Data from NIWA for today
tide_data = get_tide_data(NIWA_URL, niwa_api_key, LATITUDE, LONGTITUDE)

utc_offset = get_utc_offset( TIMEZONE_DB_URL, timezone_db_api_key )
print( "UTC offset =", utc_offset )

tide_vals = tide_data["values"]
print(tide_vals)
first_time = tide_vals[0]["time"]
current_dt = convert_to_local_time(first_time, utc_offset)
current_date = current_dt.ctime()
print( "Date = ", current_date)


displayio.release_displays()

display_bus, display, group = setup_display()


cd = current_date[:10]
display_text( display, group, LINE_START,10, "Lyttleton")
display_text( display, group, LINE_START+DATE_OFFSET, 10, cd)

# Loop over all high and low tides and display a string for each one:
ypos = 15
for val in tide_vals:
    tide_dt = convert_to_local_time( val["time"], utc_offset )
    tide_time = tide_dt.time()
    height = float(val["value"])
    tide_hi_low = ""
    if height < 1.0:
        tide_high_low = "Low "
    else:
        tide_high_low = "High"
    disp_string = "{} - {:02d}:{:02d}  {:04.2f}m ".format(tide_high_low, tide_time.hour, tide_time.minute, height)
    ypos += LINE_INCREMENT
    display_text( display, group, LINE_START + TIDE_LINE_OFFSET, ypos, disp_string, scale=2)




update_display( display, group )


print('Done, sleeping')

# Create a an alarm that will trigger 24 hours  from now.
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + SLEEP_TIME)
# Exit the program, and then deep sleep until the alarm wakes us.
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
# Does not return, so we never get here.


