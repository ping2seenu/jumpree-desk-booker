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
BOOK_DATE = tomorrow.strftime("%d %b %Y")

# Chrome Options for GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)

# Open portal
driver.get(URL)

# Login
wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "login").click()

# Booking page
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Book')]"))).click()

# Date
wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{BOOK_DATE}']"))).click()

# Floor defaulted
# Time slot defaulted

# Desk
wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(.,'{DESK_NUMBER}')]"))).click()

# Next + Book Now
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Next')]"))).click()
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Book Now')]"))).click()

print("✅ Desk booked successfully")
time.sleep(2)
driver.quit()
