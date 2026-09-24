# TideClock
TideClock - based on FeatherS2 and EInk Featherwing

Shows the day's high and low tides for Lyttleton on a 2.9" tri-colour eInk display,
then deep sleeps until around 3am local time to refresh for the next day.

## Setup

Runs on CircuitPython, including version 7 and later. Create a `secrets.py` on the board containing:

```python
secrets = {
    "ssid": "...",
    "password": "...",
    "niwa_api_key": "...",          # https://developer.niwa.co.nz
    "timezone_db_api_key": "...",   # https://timezonedb.com
}
```

## How it works

1. Connects to Wi-Fi.
2. Fetches today's tides from the NIWA Tides API.
3. Fetches the local UTC offset and hour from TimezoneDB (over https).
4. Draws each tide's local time and height, labelling it High or Low by
   comparing it with the tides either side.
5. Deep sleeps until around 3am.

## Error handling

If any step fails (Wi-Fi, either API, or updating the display), the error is
printed to the serial console and the board sleeps for one hour before trying
again. The display keeps showing the last successful update. The Wi-Fi password
and API keys are not written to the serial log.
