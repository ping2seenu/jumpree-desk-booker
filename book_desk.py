from appium import webdriver
from time import sleep
from datetime import datetime, timedelta
import os

# Credentials
USERNAME = os.getenv("JUMPREE_USER")
PASSWORD = os.getenv("JUMPREE_PASS")

# Config
FLOOR = "06"
DESK_NUMBER = "177"

# Date logic (skip weekends)
tomorrow = datetime.today() + timedelta(days=4)
while tomorrow.weekday() >= 5:
    tomorrow += timedelta(days=1)

BOOKING_DATE = tomorrow.strftime("%d %b %Y")

print("Booking Details")
print("Floor:", FLOOR)
print("Desk:", DESK_NUMBER)
print("Date:", BOOKING_DATE)

caps = {
    "platformName": "Android",
    "deviceName": "Android Emulator",
    "automationName": "UiAutomator2",
    "appPackage": "com.jumpree.app",
    "appActivity": "com.jumpree.MainActivity"
}

driver = webdriver.Remote("https://juliusbaer.smartenspaces.com", caps)
sleep(10)

# Login
driver.find_element("id","username").send_keys(USERNAME)
driver.find_element("id","password").send_keys(PASSWORD)
driver.find_element("id","login").click()
sleep(5)

# Open booking
driver.find_element("xpath","//text()='Book Desk'").click()

# Select date
driver.find_element("xpath", f"//text()='{BOOKING_DATE}'").click()

# Select floor
driver.find_element("xpath", f"//text()='{FLOOR}'").click()
sleep(2)

# Select desk
driver.find_element("xpath", f"//text()='{DESK_NUMBER}'").click()

# Confirm
driver.find_element("xpath","//text()='Confirm'").click()

print("✅ Desk booked successfully")

driver.quit()
