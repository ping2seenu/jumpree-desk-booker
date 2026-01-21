import os
import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- HARD CODE CONFIG ----------------
JUMPREE_URL = "https://juliusbaer.smartenspaces.com"
LEVEL = "Level 6"
DESK = "L6-177"
# --------------------------------------------------

USERNAME = os.getenv("JUMPREE_USERNAME")
PASSWORD = os.getenv("JUMPREE_PASSWORD")

if not USERNAME:
    raise Exception("❌ JUMPREE_USERNAME secret missing")

if not PASSWORD:
    raise Exception("❌ JUMPREE_PASSWORD secret missing")

# Booking date = today + 4 days
BOOK_DATE = (datetime.now() + timedelta(days=4)).strftime("%d/%m/%Y")

print("🚀 Jumpree automation started")
print("📅 Booking date:", BOOK_DATE)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)


def js_click(el):
    driver.execute_script("arguments[0].click();", el)


# ---------------- LOGIN ----------------
try:
    driver.get(JUMPREE_URL)
    time.sleep(5)

    # Switch iframe if exists
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print("🔁 Switching iframe")
        driver.switch_to.frame(iframes[0])

    # Username
    user = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[contains(@type,'email') or contains(@placeholder,'Email')]"
    )))
    user.send_keys(USERNAME)

    # Password
    pwd = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[contains(@type,'password')]"
    )))
    pwd.send_keys(PASSWORD)

    # Login button
    login_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[contains(text(),'Login') or contains(text(),'Sign')]"
    )))
    js_click(login_btn)

    driver.switch_to.default_content()

    wait.until(EC.presence_of_element_located((By.ID, "integration_link")))
    print("✅ Logged in")

except Exception as e:
    print("❌ Login failed:", e)
    raise


# ---------------- BOOKING ----------------
try:
    amenity = wait.until(
        EC.presence_of_element_located((By.ID, "amenity_booking"))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", amenity)
    time.sleep(2)

    try:
        amenity.click()
    except:
        print("⚠ Overlay click issue – using JS")
        js_click(amenity)

    print("➡ Opened booking page")

    # Date
    date_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select Date']"))
    )
    date_input.clear()
    date_input.send_keys(BOOK_DATE)
    time.sleep(2)

    # Level
    level_dd = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//mat-select[@formcontrolname='floor']"))
    )
    js_click(level_dd)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(),'{LEVEL}')]"))
    ).click()

    # Desk
    desk_dd = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//mat-select[@formcontrolname='seat']"))
    )
    js_click(desk_dd)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(),'{DESK}')]"))
    ).click()

    # Book
    book_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Book')]"))
    )
    js_click(book_btn)

    print("🎉 Desk booked successfully")

except Exception as e:
    print("❌ Booking failed:", e)
    raise

finally:
    time.sleep(5)
    driver.quit()
