import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIGURATION =================
EMAIL = "srinivasareddy.kumbagiri@juliusbaer.com"  # Replace with your email
PASSWORD = "Forgot@123"            # Replace with your password
URL = "https://juliusbaer.smartenspaces.com/spacemanagementV2/#/"

# Target Details
TARGET_FLOOR = "Level 06"
TARGET_DESK = "177"
START_TIME = "09:00 AM"
END_TIME = "06:00 PM"
# =================================================

def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)  # Keep browser open after script finishes
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver, wait):
    print("--- Navigating to Login ---")
    driver.get(URL)

    # 1. Enter Email
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[type='email']")))
    email_field.send_keys(EMAIL)

    # Click Proceed
    proceed_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed')]")))
    proceed_btn.click()

    # 2. Enter Password
    pass_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    pass_field.send_keys(PASSWORD)

    # 3. Click "I Agree" Terms Checkbox
    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        driver.execute_script("arguments[0].click();", checkbox)
    except:
        print("Could not click checkbox via JS, trying standard click")

    # Click Login
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]")))
    login_btn.click()
    print("--- Login Submitted ---")

def navigate_to_booking(driver, wait):
    print("--- Navigating to Booking ---")
    book_now_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Desks')]/..//button[contains(text(), 'Book Now')]")))
    book_now_btn.click()

def make_booking(driver, wait):
    print("--- Setting up Booking Details ---")

    # 1. Select Tomorrow's Date
    tomorrow = datetime.now() + timedelta(days=4)
    formatted_date = tomorrow.strftime("%d %b %Y")  # e.g., "25 Jan 2026"

    # 2. Select Floor (Level 06)
    try:
        floor_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{TARGET_FLOOR}')]")))
    except:
        print(f"Floor selection might already be set or selector needs update.")

    # 3. Set Start & End Time
    print(f"--- Setting Time: {START_TIME} to {END_TIME} ---")

    # PSEUDO-CODE for Time Selection (Update XPATH as needed)
    # start_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[1]")
    # start_time_dropdown.click()
    # select_start = driver.find_element(By.XPATH, f"//span[contains(text(), '{START_TIME}')]")
    # select_start.click()

    # end_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[2]")
    # end_time_dropdown.click()
    # select_end = driver.find_element(By.XPATH, f"//span[contains(text(), '{END_TIME}')]")
    # select_end.click()

    # 4. Select Date (Tomorrow)
    date_picker = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Date']")))
    date_picker.clear()
    date_picker.send_keys(formatted_date)
    date_picker.send_keys(Keys.RETURN)

    # 5. Click Next
    try:
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Search')]")))
        next_btn.click()
    except:
        print("No Next button found, proceeding to map...")

    # 6. Select Desk 177 (List View)
    print(f"--- Searching for Desk {TARGET_DESK} ---")
    try:
        list_view_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fa-list, .icon-list, button[title='List View']")))
        list_view_btn.click()
        print("Switched to List View")

        search_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']")))
        search_box.send_keys(TARGET_DESK)
        time.sleep(2)  # Wait for filter

        book_desk_btn = driver.find_element(By.XPATH, f"//div[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]")
        book_desk_btn.click()

    except Exception as e:
        print("Could not use List View, manual intervention required for map.")
        print(e)
        return

    # 7. Final Confirmation
    print("--- Confirming Booking ---")
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]")))
    confirm_btn.click()
    print(f"SUCCESS: Booking Confirmed for {formatted_date}!")

def main():
    driver = start_browser()
    wait = WebDriverWait(driver, 15)

    try:
        login(driver, wait)
        time.sleep(5)  # Wait for dashboard animation
        navigate_to_booking(driver, wait)
        time.sleep(3)  # Wait for booking page load
        make_booking(driver, wait)

    except Exception as e:
        print("An error occurred:")
        print(e)
    finally:
        # driver.quit()  # Uncomment to close browser automatically
        pass

if __name__ == "__main__":
    main()
