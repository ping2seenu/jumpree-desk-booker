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
EMAIL = "srinivasareddy.kumbagiri@juliusbaer.com"
PASSWORD = "Forgot@123"
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
    # Keep browser open after script finishes (good for testing)
    options.add_experimental_option("detach", True) 
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
    # Note: Sometimes checkboxes are hidden, clicking the label often works better
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
    # Wait for Dashboard to load and click "Book Now" under Desks
    # Based on screenshot 3
    print("--- Navigating to Booking ---")
    book_now_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Desks')]/..//button[contains(text(), 'Book Now')]")))
    book_now_btn.click()

def make_booking(driver, wait):
    print("--- Setting up Booking Details ---")
    
    # 1. Select Floor (Level 06)
    # This usually involves clicking a dropdown arrow, then selecting the text
    # You might need to inspect the 'Level 06' dropdown arrow ID
    try:
        # Example logic: Find the floor dropdown, click it, find text "Level 06"
        floor_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{TARGET_FLOOR}')]"))) 
        # If it's already selected, great. If not, this logic needs adjustment based on the specific dropdown HTML.
    except:
        print(f"Floor selection might already be set or selector needs update.")

    # 2. Set Start Time
    # Based on Screenshot 4 & 6
    print(f"--- Setting Time: {START_TIME} to {END_TIME} ---")
    
    # We need to find the Start Time Dropdown. 
    # Look for the dropdown that likely contains current time or "08:45 PM" as seen in screenshot
    # This is tricky without HTML, usually requires finding the select box by index
    
    # PSEUDO-CODE for Time Selection (You must update XPATH):
    # start_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[1]")
    # start_time_dropdown.click()
    # select_start = driver.find_element(By.XPATH, f"//span[contains(text(), '{START_TIME}')]")
    # select_start.click()
    
    # end_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[2]")
    # end_time_dropdown.click()
    # select_end = driver.find_element(By.XPATH, f"//span[contains(text(), '{END_TIME}')]")
    # select_end.click()

    # 3. Select Date
    # Click the calendar icon or ensure the date is correct. 
    # For "Daily", you would run this script in a loop. For now, let's select "Tomorrow"
    
    # Click Next (Screenshot 5 shows a Next button)
    try:
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Search')]")))
        next_btn.click()
    except:
        print("No Next button found, proceeding to map...")

    # 4. Select Desk 177
    print(f"--- Searching for Desk {TARGET_DESK} ---")
    
    # CRITICAL: Do not try to click the Map (CAD drawing). It is very hard to automate.
    # Look at Screenshot 4/6: There is a LIST VIEW icon (top right, usually 3 lines or a list icon).
    # We want to switch to List View.
    
    try:
        # Try to find the List View toggle button. 
        # Inspect the icon in the top right next to the map filters.
        list_view_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fa-list, .icon-list, button[title='List View']"))) 
        list_view_btn.click()
        print("Switched to List View")
        
        # Now search for the desk
        search_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']")))
        search_box.send_keys(TARGET_DESK)
        time.sleep(2) # Wait for filter
        
        # Click the "Book" button next to the result
        book_desk_btn = driver.find_element(By.XPATH, f"//div[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]")
        book_desk_btn.click()
        
    except Exception as e:
        print("Could not use List View, manual intervention required for map.")
        print(e)
        return

    # 5. Final Confirmation
    print("--- Confirming Booking ---")
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]")))
    confirm_btn.click()
    print("SUCCESS: Booking Confirmed!")

def main():
    driver = start_browser()
    wait = WebDriverWait(driver, 15)
    
    try:
        login(driver, wait)
        
        # Wait for dashboard animation
        time.sleep(5) 
        
        navigate_to_booking(driver, wait)
        
        # Wait for booking page load
        time.sleep(3)
        
        make_booking(driver, wait)
        
    except Exception as e:
        print("An error occurred:")
        print(e)
    finally:
        # driver.quit() # Uncomment this to close browser automatically
        pass

if __name__ == "__main__":
    main()
