import os
from utils.helpers import parse_bool_value

class Config:
    PIXOO_HOST = os.getenv("PIXOO_HOST", "192.168.1.100")
    PIXOO_SCREEN_SIZE = int(os.getenv("PIXOO_SCREEN_SIZE", 64))
    PIXOO_DEBUG = parse_bool_value(os.getenv("PIXOO_DEBUG", "false"))
    ANIMATION_FRAME_DELAY = float(os.getenv("ANIMATION_FRAME_DELAY", 0.5))
    CSV_FILE_PATH = "dataset/data.csv"
    CSV_BEER_FILE_PATH = "dataset/beer_data.csv"
    COUNTRY_TIMEZONES = {
        "Australia": "Australia/Sydney",
        "Philippines": "Asia/Manila",
        "United States": "America/New_York",
        "India": "Asia/Kolkata",
        "Colombia": "America/Bogota",
    }

    DIFY_API_KEY = os.getenv('DIFY_API_KEY', '')
    DIFY_API_URL = os.getenv('DIFY_API_URL', 'https://aibot.cloudstaff.io/v1/chat-messages')