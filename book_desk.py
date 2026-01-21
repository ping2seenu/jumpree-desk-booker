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

# None = first available desk
DESK_NUMBER = None

# =========================================

USERNAME = os.getenv("JUMPREE_USERNAME")
PASSWORD = os.getenv("JUMPREE_PASSWORD")

if not USERNAME:
    raise Exception("❌ JUMPREE_USERNAME secret missing")
if not PASSWORD:
    raise Exception("❌ JUMPREE_PASSWORD secret missing")

# Browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

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

    # --- FIXED Angular checkbox ---
    checkbox = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//mat-checkbox[@id='acceptTerms']//div[contains(@class,'mat-checkbox-inner-container')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    checkbox.click()
    print("☑ Terms accepted")

    # Login
    driver.find_element(By.ID, "submit_btn").click()

    # ---------------- BOOKING ----------------

    wait.until(EC.element_to_be_clickable((By.ID, "amenity_booking"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "book_now_amenity"))).click()

    # Open calendar
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@src,'calendar_icon')]"))
    ).click()

    # -------- DATE (Today + 4) --------
    target = datetime.today() + timedelta(days=4)
    day = target.day

    print("📅 Booking date:", target.strftime("%d-%m-%Y"))

    date_xpath = f"//td//div[text()='{day}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
    # ---------------------------------

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
        desk_xpath = f"//span[text()='{DESK_NUMBER}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, desk_xpath))).click()
    else:
        print("🎯 Selecting first available desk")
        desk = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@class,'leaflet-marker-icon')]")
        ))
        desk.click()

    # Final book
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
