from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import os
import time

# ---- CONFIG ----
URL = "https://juliusbaer.smartenspaces.com"
USERNAME = os.getenv("JUMPREE_USER")
PASSWORD = os.getenv("JUMPREE_PASS")
DESK_NUMBER = os.getenv("DESK_NUMBER", "177")
FLOOR_DEFAULT = os.getenv("FLOOR", "6")
TIME_SLOT_DEFAULT = "09:00-18:00"  # defaulted in portal

# ---- TOMORROW'S DATE ----
tomorrow = datetime.today() + timedelta(days=4)
BOOK_DATE = tomorrow.strftime("%d %b %Y")
print("Booking Details:")
print("Date:", BOOK_DATE)
print("Desk:", DESK_NUMBER)
print("Floor:", FLOOR_DEFAULT)
print("Time:", TIME_SLOT_DEFAULT)

# ---- CHROME OPTIONS ----
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # works in GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
wait = WebDriverWait(driver, 30)

# ---- OPEN PORTAL ----
driver.get(URL)
time.sleep(5)  # wait for portal to fully load

# ---- LOGIN ----
try:
    # Try common username input locators
    username_input = wait.until(
        EC.presence_of_element_located((
            By.XPATH, "//input[@type='text' or @name='username' or contains(@placeholder,'Username')]"
        ))
    )
    username_input.send_keys(USERNAME)

    password_input = driver.find_element(
        By.XPATH, "//input[@type='password' or @name='password' or contains(@placeholder,'Password')]"
    )
    password_input.send_keys(PASSWORD)

    # Click login button
    login_btn = driver.find_element(
        By.XPATH, "//button[contains(.,'Login') or contains(.,'Sign in')]"
    )
    login_btn.click()
except Exception as e:
    print("❌ Login failed:", e)
    driver.save_screenshot("login_error.png")
    driver.quit()
    exit(1)

# ---- OPEN BOOKING PAGE ----
try:
    book_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Book')]"))
    )
    book_btn.click()
except Exception as e:
    print("❌ Could not open booking page:", e)
    driver.save_screenshot("booking_page_error.png")
    driver.quit()
    exit(1)

# ---- SELECT DATE ----
try:
    date_elem = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//span[text()='{BOOK_DATE}']"))
    )
    date_elem.click()
except Exception as e:
    print("❌ Could not select date:", e)
    driver.save_screenshot("date_error.png")
    driver.quit()
    exit(1)

# ---- FLOOR AND TIME ----
# Skip, defaulted in portal

# ---- SELECT DESK ----
try:
    desk_elem = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//span[contains(.,'{DESK_NUMBER}')]"))
    )
    desk_elem.click()
except Exception as e:
    print("❌ Could not select desk:", e)
    driver.save_screenshot("desk_error.png")
    driver.quit()
    exit(1)

# ---- NEXT AND BOOK NOW ----
try:
    next_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Next')]"))
    )
    next_btn.click()

    book_now_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Book Now')]"))
    )
    book_now_btn.click()
except Exception as e:
    print("❌ Could not finalize booking:", e)
    driver.save_screenshot("book_now_error.png")
    driver.quit()
    exit(1)

print("✅ Desk booked successfully!")
driver.quit()
