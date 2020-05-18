import requests

BASE = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(latitude, longitude, timeout=1, api_key="f3f35c105957cbc06255077f3839668c"):

    if api_key is None:
        return None

    url = BASE + "?units=metric&lat={}&lon={}&appid={}".format(
        latitude, longitude, api_key)

    try:
        # print(url)
        r = requests.get(url, timeout=timeout)
        return r.json()
    except:
        # Usually Timeout
        return None
