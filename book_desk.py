from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import os
import time

# Config
URL = "https://juliusbaer.smartenspaces.com"
USERNAME = os.getenv("JUMPREE_USER")
PASSWORD = os.getenv("JUMPREE_PASS")
DESK_NUMBER = os.getenv("DESK_NUMBER", "177")
FLOOR_DEFAULT = "6"
TIME_SLOT_DEFAULT = "09:00-18:00"

# Next day
tomorrow = datetime.today() + timedelta(days=4)
BOOK_DATE = tomorro_
