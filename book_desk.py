import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

# ================= CONFIGURATION =================
EMAIL = os.getenv("BOOKING_EMAIL", "srinivasareddy.kumbagiri@juliusbaer.com")
PASSWORD = os.getenv("BOOKING_PASSWORD", "Forgot@123")
URL = "https://juliusbaer.smartenspaces.com/spacemanagementV2/#/"

# Target Details
TARGET_FLOOR = "Level 06"
TARGET_DESK = "177"
START_TIME = "09:00 AM"
END_TIME = "06:00 PM"
DAYS_AHEAD = 4  # Book 4 days in advance
# =================================================

def start_browser():
    """Initialize Chrome with CI/headless-friendly options"""
    options = Options()
    
    # Check if running in CI environment
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    
    if is_ci:
        print("🤖 Running in CI mode (headless)")
        options.add_argument("--headless=new")
    else:
        print("🖥️  Running in local mode (headed)")
    
    # Essential options for both local and CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Avoid detection as bot
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Keep browser open only in local mode
    if not is_ci:
        options.add_experimental_option("detach", True)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Anti-detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def login(driver, wait):
    """Handle login flow"""
    print("--- Navigating to Login ---")
    driver.get(URL)
    time.sleep(2)  # Let page load

    try:
        # 1. Enter Email
        email_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[type='email']"))
        )
        email_field.clear()
        email_field.send_keys(EMAIL)
        print(f"✅ Email entered: {EMAIL}")

        # Click Proceed
        proceed_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed')]"))
        )
        proceed_btn.click()
        time.sleep(1)

        # 2. Enter Password
        pass_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
        )
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        print("✅ Password entered")

        # 3. Click "I Agree" Terms Checkbox (if present)
        try:
            checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)
                print("✅ Terms checkbox clicked")
        except Exception as e:
            print(f"⚠️  No checkbox found (may not be required): {e}")

        # Click Login
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_btn.click()
        print("✅ Login submitted")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.save_screenshot("login_error.png")
        raise

def navigate_to_booking(driver, wait):
    """Navigate to desk booking section"""
    print("--- Navigating to Booking ---")
    try:
        book_now_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Desks')]/..//button[contains(text(), 'Book Now')]")
            )
        )
        book_now_btn.click()
        print("✅ Clicked Book Now")
    except Exception as e:
        print(f"❌ Could not find Book Now button: {e}")
        driver.save_screenshot("booking_nav_error.png")
        raise

def make_booking(driver, wait):
    """Complete the booking process"""
    print("--- Setting up Booking Details ---")

    try:
        # 1. Calculate target date
        target_date = datetime.now() + timedelta(days=DAYS_AHEAD)
        formatted_date = target_date.strftime("%d %b %Y")  # e.g., "25 Jan 2026"
        print(f"📅 Target Date: {formatted_date}")

        # 2. Select Floor (if needed)
        try:
            floor_dropdown = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{TARGET_FLOOR}')]"))
            )
            floor_dropdown.click()
            print(f"✅ Floor selected: {TARGET_FLOOR}")
        except:
            print(f"⚠️  Floor selection might already be set to {TARGET_FLOOR}")

        # 3. Set Date
        try:
            date_picker = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Date']"))
            )
            date_picker.clear()
            date_picker.send_keys(formatted_date)
            date_picker.send_keys(Keys.RETURN)
            time.sleep(1)
            print(f"✅ Date set: {formatted_date}")
        except Exception as e:
            print(f"⚠️  Date picker issue: {e}")

        # 4. Set Time (uncomment and adjust selectors as needed)
        """
        print(f"--- Setting Time: {START_TIME} to {END_TIME} ---")
        start_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[1]")
        start_time_dropdown.click()
        select_start = driver.find_element(By.XPATH, f"//span[contains(text(), '{START_TIME}')]")
        select_start.click()

        end_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[2]")
        end_time_dropdown.click()
        select_end = driver.find_element(By.XPATH, f"//span[contains(text(), '{END_TIME}')]")
        select_end.click()
        print("✅ Time set")
        """

        # 5. Click Next/Search
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Search')]")
                )
            )
            next_btn.click()
            time.sleep(2)
            print("✅ Clicked Next")
        except:
            print("⚠️  No Next button found, proceeding...")

        # 6. Select Desk 177 (List View)
        print(f"--- Searching for Desk {TARGET_DESK} ---")
        try:
            # Switch to List View
            list_view_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".fa-list, .icon-list, button[title='List View']")
                )
            )
            list_view_btn.click()
            time.sleep(1)
            print("✅ Switched to List View")

            # Search for desk
            search_box = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search']"))
            )
            search_box.clear()
            search_box.send_keys(TARGET_DESK)
            time.sleep(2)  # Wait for filter
            print(f"✅ Searched for desk: {TARGET_DESK}")

            # Book the desk
            book_desk_btn = driver.find_element(
                By.XPATH, f"//div[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]"
            )
            book_desk_btn.click()
            print(f"✅ Clicked Book for Desk {TARGET_DESK}")

        except Exception as e:
            print(f"❌ Could not find/book desk: {e}")
            driver.save_screenshot("desk_selection_error.png")
            raise

        # 7. Final Confirmation
        print("--- Confirming Booking ---")
        confirm_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]")
            )
        )
        confirm_btn.click()
        time.sleep(2)
        print(f"🎉 SUCCESS: Booking Confirmed for {formatted_date}!")

    except Exception as e:
        print(f"❌ Booking failed: {e}")
        driver.save_screenshot("booking_error.png")
        raise

def main():
    driver = None
    try:
        driver = start_browser()
        wait = WebDriverWait(driver, 20)

        login(driver, wait)
        time.sleep(5)  # Wait for dashboard animation
        
        navigate_to_booking(driver, wait)
        time.sleep(3)  # Wait for booking page load
        
        make_booking(driver, wait)
        
        print("\n✅ Script completed successfully!")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        if driver:
            driver.save_screenshot("final_error.png")
            print("📸 Screenshot saved as final_error.png")
        raise
        
    finally:
        # Only close in CI mode
        if driver and os.getenv("CI") == "true":
            driver.quit()
            print("🔒 Browser closed")
        elif driver:
            print("🖥️  Browser left open for inspection")

if __name__ == "__main__":
    main()
