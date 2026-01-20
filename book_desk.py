import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
URL = "https://juliusbaer.smartenspaces.com/spacemanagementV2/#/"
EMAIL = "srinivasareddy.kumbagiri@juliusbaer.com"
PASSWORD = "Forgot@123"
FLOOR = "Level 06"
DESK_ID = "177"
START_TIME = "09:00 AM"
END_TIME = "06:00 PM"

def run_booking():
    # Setup Chrome
    options = Options()
    # options.add_argument("--headless") # Uncomment to run without opening a window
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(URL)
        driver.maximize_window()

        # 1. LOGIN PHASE
        print("Logging in...")
        email_input = wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        email_input.send_keys(EMAIL)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Proceed')]").click()

        pass_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        pass_input.send_keys(PASSWORD)
        
        # Click I agree checkbox
        driver.find_element(By.XPATH, "//span[contains(text(), 'I agree')]").click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        # 2. NAVIGATE TO BOOKING
        print("Navigating to Desk Booking...")
        booking_sidebar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Booking']")))
        booking_sidebar.click()
        
        book_now_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Book Now')]")))
        book_now_btn.click()

        # 3. SELECT FLOOR & TIME
        print(f"Selecting {FLOOR} and time...")
        # Select Floor (Level 06)
        floor_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'location-select')]")))
        floor_dropdown.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{FLOOR}']"))).click()

        # Select Times
        # Note: These are usually custom dropdowns. This clicks the dropdown and selects the time text.
        start_dropdown = driver.find_elements(By.XPATH, "//div[contains(@class, 'mat-select-arrow-wrapper')]")[0]
        start_dropdown.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{START_TIME}')]"))).click()
        
        end_dropdown = driver.find_elements(By.XPATH, "//div[contains(@class, 'mat-select-arrow-wrapper')]")[1]
        end_dropdown.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{END_TIME}')]"))).click()

        # 4. CALENDAR DATE SELECTION (Selects Tomorrow by default)
        # To do 'Daily', you'd loop through available dates here
        print("Selecting date...")
        calendar_icon = driver.find_element(By.XPATH, "//mat-icon[text()='calendar_today']")
        calendar_icon.click()
        
        # This part depends on the calendar structure. 
        # Clicking the first available 'green' (available) date:
        available_date = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".available-date-class"))) 
        available_date.click()
        driver.find_element(By.XPATH, "//button[text()='Next']").click()

        # 5. DESK SELECTION (The crucial part)
        print(f"Finding Desk {DESK_ID}...")
        # Toggle to List View (The icon with dots and lines)
        list_view_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-icon[text()='list']")))
        list_view_btn.click()

        # Find Desk 177 in the list
        desk_item = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{DESK_ID}')]")))
        desk_item.click()

        # 6. CONFIRMATION
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm')]")))
        confirm_btn.click()
        
        print("Booking Successful!")
        time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_booking()
