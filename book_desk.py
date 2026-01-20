from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta
import os
import time

URL = "https://juliusbaer.smartenspaces.com"

USERNAME = os.getenv("JUMPREE_USER")
PASSWORD = os.getenv("JUMPREE_PASS")

FLOOR = "06"
DESK = "177"

# Date logic
tomorrow = datetime.today() + timedelta(days=1)
while tomorrow.weekday() >= 5:
    tomorrow += timedelta(days=1)

BOOK_DATE = tomorrow.strftime("%d %b %Y")

print("Booking Details")
print("Floor:", FLOOR)
print("Desk:", DESK)
print("Date:", BOOK_DATE)

options = webdriver.ChromeOptions()
options.add_argument("--headless")   # remove if you want UI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)

driver.get(URL)

# -------- LOGIN --------
wait.until(EC.presence_of_element_located((By.ID,"username"))).send_keys(USERNAME)
driver.find_element(By.ID,"password").send_keys(PASSWORD)
driver.find_element(By.ID,"login").click()

# -------- BOOK DESK --------
wait.until(EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Book')]"))).click()

# Select date
wait.until(EC.element_to_be_clickable((
    By.XPATH, f"//span[text()='{BOOK_DATE}']"
))).click()

# Select floor
wait.until(EC.element_to_be_clickable((
    By.XPATH, f"//span[contains(.,'{FLOOR}')]"
))).click()

# Select desk
wait.until(EC.element_to_be_clickable((
    By.XPATH, f"//span[contains(.,'{DESK}')]"
))).click()

# Confirm
wait.until(EC.element_to_be_clickable((
    By.XPATH,"//button[contains(.,'Confirm')]"
))).click()

print("✅ Desk booked successfully")

time.sleep(3)
driver.quit()
