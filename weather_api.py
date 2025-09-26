import os, requests
from dotenv import load_dotenv
load_dotenv()

BASE = "https://api.weatherapi.com/v1"
KEY = os.getenv("WEATHERAPI_KEY")

def get_current_weather(q="Santiago"):
    return requests.get(f"{BASE}/current.json", params={"key":KEY,"q":q,"aqi":"no"}).json()

def get_forecast(q="Santiago", days=1):
    return requests.get(f"{BASE}/forecast.json", params={"key":KEY,"q":q,"days":days,"aqi":"no","alerts":"no"}).json()
