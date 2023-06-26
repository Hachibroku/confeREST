import json
import requests
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"per_page": 1, "query": f"{city}, {state}"}
    url = "https://api.pexels.com/v1/search"
    response = requests.get(url, params=params, headers=headers)
    content = json.loads(response.content)
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_lat_long(city, state):
    params = {
        "q": f"{city}, {state}, US",
        "limit": 1,
        "appid": OPEN_WEATHER_API_KEY,
    }
    url = "http://api.openweathermap.org/geo/1.0/direct"
    response = requests.get(url, params=params)
    content = json.loads(response.content)
    if isinstance(content, list):
        first_elem = content[0]
    else:
        first_elem = content
    try:
        return {"lat": first_elem["lat"], "lon": first_elem["lon"]}
    except (KeyError, IndexError):
        lat_lon = {
            "lat": None,
            "lon": None,
        }
        return lat_lon


def get_weather_data(city, state):
    lat_lon = get_lat_long(city, state)
    params = {
        "lat": lat_lon["lat"],
        "lon": lat_lon["lon"],
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial",
    }
    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(url, params=params)
    content = json.loads(response.content)
    try:
        return {
            "temp": content["main"]["temp"],
            "description": content["weather"][0]["description"],
        }
    except (KeyError, IndexError):
        weather = {"temp": None, "description": None}
        return weather
