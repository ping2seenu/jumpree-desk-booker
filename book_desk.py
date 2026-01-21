from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ================= HARDCODE CONFIG =================

JUMPREE_URL = "https://juliusbaer.smartenspaces.com"
LOCATION = "ONE@CHANGI CITY"
LEVEL = "Level 06"

# Optional: desk number (None = first available)
DESK_NUMBER = "06-177"   # Example: "D-12"

# ====================================================

# Secrets
USERNAME = os.getenv("JUMPREE_USERNAME")
PASSWORD = os.getenv("JUMPREE_PASSWORD")

# Validate secrets
if not USERNAME:
    raise Exception("❌ JUMPREE_USERNAME secret missing")
if not PASSWORD:
    raise Exception("❌ JUMPREE_PASSWORD secret missing")

# Browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)

try:
    print("🚀 Jumpree automation started")

    driver.get(JUMPREE_URL)

    # ---------------- LOGIN ----------------
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "submit_btn").click()

    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)

    terms = wait.until(EC.element_to_be_clickable((By.ID, "acceptTerms-input")))
    if not terms.is_selected():
        terms.click()

    driver.find_element(By.ID, "submit_btn").click()

    # ---------------- BOOKING ----------------
    wait.until(EC.element_to_be_clickable((By.ID, "amenity_booking"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "book_now_amenity"))).click()

    # Calendar
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@src,'calendar_icon')]"))
    ).click()

    # ---------- DATE LOGIC ----------
    target = datetime.today() + timedelta(days=4)
    day = target.day
    print("📅 Booking date:", target.strftime("%d-%m-%Y"))

    date_xpath = f"//td//div[text()='{day}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
    # --------------------------------

    # Next
    driver.find_element(By.XPATH, "//button[text()='Next']").click()

    # Location
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//p[contains(text(),'{LOCATION}')]"))
    ).click()

    # Level
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//p[contains(text(),'{LEVEL}')]"))
    ).click()

    # ---------------- DESK ----------------
    if DESK_NUMBER:
        print("🎯 Selecting desk:", DESK_NUMBER)
        desk_xpath = f"//span[text()='{DESK_NUMBER}']/ancestor::div[contains(@class,'desk')]"
        wait.until(EC.element_to_be_clickable((By.XPATH, desk_xpath))).click()
    else:
        print("🎯 Selecting first available desk")
        desk = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@class,'leaflet-marker-icon')]")
        ))
        desk.click()

    # Final Book
    wait.until(EC.element_to_be_clickable(
        (By.ID, "save_booking"))
    ).click()

    print("✅ DESK BOOKED SUCCESSFULLY!")

except Exception as e:
    print("❌ Booking failed:", e)
    raise

finally:
    time.sleep(5)
    driver.quit()
