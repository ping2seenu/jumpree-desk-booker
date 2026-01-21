from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ---------- CONFIG ----------
URL = "https://jumpree.smartenspaces.com"

EMAIL = os.getenv("JUMPREE_EMAIL")
PASSWORD = os.getenv("JUMPREE_PASSWORD")

HEADLESS = True
# ----------------------------

options = webdriver.ChromeOptions()

if HEADLESS:
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)

try:
    print("🚀 Starting Jumpree booking")

    driver.get(URL)

    # Email
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
    driver.find_element(By.ID, "submit_btn").click()

    # Password
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)

    # Accept terms
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
    print("📅 Booking for:", target.strftime("%d-%m-%Y"))

    date_xpath = f"//td//div[text()='{day}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
    # --------------------------------

    # Next
    driver.find_element(By.XPATH, "//button[text()='Next']").click()

    # Location
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//p[contains(text(),'ONE@CHANGI CITY')]"))
    ).click()

    # Floor
    driver.find_element(By.XPATH, "//p[contains(text(),'Level 06')]").click()

    # Desk
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@class,'leaflet-marker-icon')]"))
    ).click()

    # Book
    wait.until(EC.element_to_be_clickable(
        (By.ID, "save_booking"))
    ).click()

    print("✅ Booking SUCCESS")

except Exception as e:
    print("❌ FAILED:", e)
    raise

finally:
    time.sleep(5)
    driver.quit()
