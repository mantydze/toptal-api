import requests

BASE = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(latitude, longitude, timeout=1, api_key=None):

    try:
        if api_key is None:
            from flask import current_app
            api_key = current_app.config["WEATHER_API_KEY"]

        url = BASE + "?units=metric&lat={}&lon={}&appid={}".format(
            latitude, longitude, api_key)

        r = requests.get(url, timeout=timeout)
        return r.json()
    except Exception:
        # Usually Timeout
        return None
