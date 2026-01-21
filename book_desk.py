from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ================= CONFIG =================

JUMPREE_URL = "https://jumpree.smartenspaces.com"
LOCATION = "ONE@CHANGI CITY"
LEVEL = "Level 06"
DESK_NUMBER = None   # Optional

# =========================================

USERNAME = os.getenv("JUMPREE_USERNAME")
PASSWORD = os.getenv("JUMPREE_PASSWORD")

if not USERNAME or not PASSWORD:
    raise Exception("❌ Secrets missing")

# ---------------- BROWSER ----------------

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Fake real browser
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 60)

# ---------------- HELPERS ----------------

def wait_page():
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

# ----------------------------------------

try:
    print("🚀 Jumpree automation started")

    driver.get(JUMPREE_URL)
    wait_page()

    # ---------- LOGIN ----------

    email = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email.send_keys(USERNAME)

    driver.find_element(By.ID, "submit_btn").click()

    pwd = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    pwd.send_keys(PASSWORD)

    # Checkbox
    checkbox = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//mat-checkbox[@id='acceptTerms']//div[contains(@class,'mat-checkbox-inner-container')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    checkbox.click()

    # Login
    driver.find_element(By.ID, "submit_btn").click()

    print("✅ Logged in")

    # ---------- BOOKING ----------

    wait.until(EC.element_to_be_clickable(
        (By.ID, "amenity_booking"))).click()

    wait.until(EC.element_to_be_clickable(
        (By.ID, "book_now_amenity"))).click()

    # Calendar
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@src,'calendar_icon')]"))
    ).click()

    # Date = Today + 4
    target = datetime.today() + timedelta(days=4)
    day = target.day

    print("📅 Booking:", target.strftime("%d-%m-%Y"))

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//td//div[text()='{day}']"))
    ).click()

    driver.find_element(By.XPATH, "//button[text()='Next']").click()

    # Location
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//p[contains(text(),'{LOCATION}')]"))
    ).click()

    # Level
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//p[contains(text(),'{LEVEL}')]"))
    ).click()

    # Desk
    if DESK_NUMBER:
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//span[text()='{DESK_NUMBER}']"))
        ).click()
    else:
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@class,'leaflet-marker-icon')]"))
        ).click()

    # Book
    wait.until(EC.element_to_be_clickable(
        (By.ID, "save_booking"))).click()

    print("🎉 DESK BOOKED SUCCESSFULLY")

except Exception as e:
    driver.save_screenshot("error.png")
    print("❌ Booking failed:", e)
    raise

finally:
    time.sleep(5)
    driver.quit()
