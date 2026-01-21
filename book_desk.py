from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# -------- LOAD FROM SECRETS ----------
URL = os.getenv("JUMPREE_URL")
USERNAME = os.getenv("JUMPREE_USERNAME")
PASSWORD = os.getenv("JUMPREE_PASSWORD")
LEVEL = os.getenv("JUMPREE_LEVEL")
LOCATION = os.getenv("JUMPREE_LOCATION")
# ------------------------------------

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)

try:
    print("🚀 Jumpree booking started")

    driver.get(URL)

    # Username
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "submit_btn").click()

    # Password
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)

    # Accept Terms
    terms = wait.until(EC.element_to_be_clickable((By.ID, "acceptTerms-input")))
    if not terms.is_selected():
        terms.click()

    # Login
    driver.find_element(By.ID, "submit_btn").click()

    # Booking menu
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

    # Desk (first available)
    desk = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@class,'leaflet-marker-icon')]"))
    )
    desk.click()

    # Book
    wait.until(EC.element_to_be_clickable(
        (By.ID, "save_booking"))
    ).click()

    print("✅ Desk booked successfully!")

except Exception as e:
    print("❌ Booking failed:", e)
    raise

finally:
    time.sleep(5)
    driver.quit()
