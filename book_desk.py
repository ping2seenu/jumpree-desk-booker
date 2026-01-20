from appium import webdriver
from time import sleep
import os

USERNAME = os.getenv("JUMPREE_USER")
PASSWORD = os.getenv("JUMPREE_PASS")

caps = {
    "platformName": "Android",
    "deviceName": "Android Emulator",
    "automationName": "UiAutomator2",
    "appPackage": "com.jumpree.app",
    "appActivity": "com.jumpree.MainActivity"
}

driver = webdriver.Remote("http://localhost:4723", caps)
sleep(10)

# Login
driver.find_element("id","username").send_keys(USERNAME)
driver.find_element("id","password").send_keys(PASSWORD)
driver.find_element("id","login").click()
sleep(5)

# Book desk
driver.find_element("xpath","//text()='Book Desk'").click()
driver.find_element("xpath","//text()='Tomorrow'").click()
driver.find_element("xpath","//text()='Confirm'").click()

print("✅ Desk booked successfully")

driver.quit()
