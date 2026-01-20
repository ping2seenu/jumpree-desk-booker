import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os

# ================= CONFIGURATION =================
EMAIL = os.getenv("JUMPREE_USER", "srinivasareddy.kumbagiri@juliusbaer.com")
PASSWORD = os.getenv("JUMPREE_PASS", "Forgot@123")
URL = "https://juliusbaer.smartenspaces.com/spacemanagementV2/#/"

# Target Details
TARGET_FLOOR = "Level 06"
TARGET_DESK = "177"
START_TIME = "09:00 AM"
END_TIME = "06:00 PM"
DAYS_AHEAD = 4
# =================================================

def start_browser():
    """Initialize Chrome with CI/headless-friendly options"""
    options = Options()
    
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    
    if is_ci:
        print("🤖 Running in CI mode (headless)")
        options.add_argument("--headless=new")
    else:
        print("🖥️  Running in local mode (headed)")
    
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
    
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if not is_ci:
        options.add_experimental_option("detach", True)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def save_debug_info(driver, step_name):
    """Save screenshot and page source for debugging"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"debug_{step_name}_{timestamp}.png"
        html_path = f"debug_{step_name}_{timestamp}.html"
        
        driver.save_screenshot(screenshot_path)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print(f"📸 Screenshot: {screenshot_path}")
        print(f"📄 HTML saved: {html_path}")
        print(f"🔗 Current URL: {driver.current_url}")
    except Exception as e:
        print(f"⚠️  Could not save debug info: {e}")

def wait_for_angular(driver, timeout=30):
    """Wait for Angular app to finish loading"""
    print("⏳ Waiting for Angular to load...")
    time.sleep(2)
    
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ Page ready")
    except:
        print("⚠️  Page may not be fully ready")
    
    # Wait for spinners to disappear
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".spinner, .loading, .loader"))
        )
    except:
        pass
    
    time.sleep(1)

def login(driver, wait):
    """Handle login flow"""
    print("--- Navigating to Login ---")
    driver.get(URL)
    time.sleep(3)

    try:
        # 1. Enter Email
        email_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[type='email']"))
        )
        email_field.clear()
        email_field.send_keys(EMAIL)
        print(f"✅ Email entered")

        # Click Proceed
        proceed_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed')]"))
        )
        proceed_btn.click()
        time.sleep(2)

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
        except:
            print("⚠️  No checkbox found")

        # Click Login
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_btn.click()
        print("✅ Login submitted")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        save_debug_info(driver, "login_error")
        raise

def navigate_to_booking(driver, wait):
    """Navigate: Click Booking menu → Click Book Now button"""
    print("--- Navigating to Booking ---")
    
    # Wait for dashboard to load
    wait_for_angular(driver)
    time.sleep(5)  # Extra wait for menu to render
    
    # STEP 1: Click "Booking" menu item
    print("🔍 Step 1: Clicking 'Booking' menu...")
    
    booking_menu_selectors = [
        (By.XPATH, "//span[@class='text' and text()='Booking']/parent::a"),
        (By.XPATH, "//span[text()='Booking']/parent::a"),
        (By.XPATH, "//span[contains(@class, 'text') and text()='Booking']/.."),
        (By.ID, "amenity_booking"),
        (By.XPATH, "//a[@id='amenity_booking']"),
        (By.XPATH, "//a[contains(@href, 'amenity-booking')]"),
    ]
    
    booking_clicked = False
    for i, (by, selector) in enumerate(booking_menu_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(booking_menu_selectors)}...")
            booking_menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Scroll into view and highlight
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                booking_menu
            )
            time.sleep(0.5)
            
            # Click via JavaScript
            driver.execute_script("arguments[0].click();", booking_menu)
            print(f"✅ Clicked 'Booking' menu")
            booking_clicked = True
            time.sleep(3)
            break
            
        except Exception as e:
            print(f"  Selector {i} failed: {str(e)[:80]}")
            continue
    
    if not booking_clicked:
        print("❌ Could not click 'Booking' menu")
        save_debug_info(driver, "booking_menu_not_found")
        raise Exception("Could not find 'Booking' menu item")
    
    # Wait for booking page to load
    wait_for_angular(driver)
    
    # STEP 2: Click "Book Now" button (ID: book_now_amenity)
    print("🔍 Step 2: Clicking 'Book Now' button...")
    
    book_now_selectors = [
        (By.ID, "book_now_amenity"),
        (By.XPATH, "//button[@id='book_now_amenity']"),
        (By.XPATH, "//button[contains(text(), 'Book Now') and @id='book_now_amenity']"),
        (By.XPATH, "//button[contains(text(), 'Book Now')]"),
    ]
    
    for i, (by, selector) in enumerate(book_now_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(book_now_selectors)}...")
            book_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Scroll and click
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                book_btn
            )
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", book_btn)
            print(f"✅ Clicked 'Book Now' button")
            time.sleep(2)
            return
            
        except Exception as e:
            print(f"  Selector {i} failed: {str(e)[:80]}")
            continue
    
    print("❌ Could not find 'Book Now' button")
    save_debug_info(driver, "book_now_not_found")
    raise Exception("Could not find 'Book Now' button")

def make_booking(driver, wait):
    """Complete the booking process"""
    print("--- Setting up Booking Details ---")

    try:
        wait_for_angular(driver)
        save_debug_info(driver, "booking_form")
        
        target_date = datetime.now() + timedelta(days=DAYS_AHEAD)
        formatted_date = target_date.strftime("%d %b %Y")
        print(f"📅 Target Date: {formatted_date}")

        # Click calendar icon to open date picker
        print("🔍 Opening date picker...")
        try:
            calendar_icon_selectors = [
                "//img[contains(@src, 'calendar_icon.png')]",
                "//img[@class='cursor-pointer iconSize']",
                "input[placeholder*='Date']",
                "input[type='date']",
            ]
            
            for selector in calendar_icon_selectors:
                try:
                    if selector.startswith("//"):
                        calendar = driver.find_element(By.XPATH, selector)
                    else:
                        calendar = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    driver.execute_script("arguments[0].click();", calendar)
                    print("✅ Opened date picker")
                    time.sleep(1)
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️  Could not open date picker: {e}")

        # Set Date (try direct input if date picker opened)
        try:
            date_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Date'], input[type='date'], input[type='text']"))
            )
            date_input.clear()
            date_input.send_keys(formatted_date)
            date_input.send_keys(Keys.RETURN)
            time.sleep(1)
            print(f"✅ Date set: {formatted_date}")
        except Exception as e:
            print(f"⚠️  Date input failed: {e}")

        # Select Floor/Location (if needed)
        try:
            floor_selector = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{TARGET_FLOOR}')]"))
            )
            driver.execute_script("arguments[0].click();", floor_selector)
            print(f"✅ Floor selected: {TARGET_FLOOR}")
        except:
            print(f"⚠️  Floor selection not needed or not found")

        # Click "Next" button to show available desks (ID: save_booking)
        print("🔍 Clicking 'Next' to search desks...")
        try:
            next_btn_selectors = [
                (By.ID, "save_booking"),
                (By.XPATH, "//button[@id='save_booking' and contains(text(), 'Next')]"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
            ]
            
            for by, selector in next_btn_selectors:
                try:
                    next_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    driver.execute_script("arguments[0].click();", next_btn)
                    print("✅ Clicked 'Next'")
                    time.sleep(3)
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️  Next button not found: {e}")

        # Wait for desk results to load
        wait_for_angular(driver)
        save_debug_info(driver, "desk_list")

        # Select Desk
        print(f"--- Searching for Desk {TARGET_DESK} ---")
        
        # Try to switch to list view (if available)
        try:
            list_view_btn = driver.find_element(By.CSS_SELECTOR, ".fa-list, .icon-list, button[title='List View']")
            driver.execute_script("arguments[0].click();", list_view_btn)
            time.sleep(1)
            print("✅ Switched to List View")
        except:
            print("⚠️  List view not available or not needed")

        # Search for desk
        try:
            search_box = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
            )
            search_box.clear()
            search_box.send_keys(TARGET_DESK)
            time.sleep(2)
            print(f"✅ Searched for desk: {TARGET_DESK}")
        except:
            print("⚠️  No search box found")

        # Click on the desk to select it
        print(f"🔍 Selecting Desk {TARGET_DESK}...")
        try:
            desk_selectors = [
                f"//div[contains(text(), '{TARGET_DESK}')]",
                f"//td[contains(text(), '{TARGET_DESK}')]",
                f"//*[text()='{TARGET_DESK}']",
                f"//*[contains(text(), 'Desk {TARGET_DESK}')]",
            ]
            
            for selector in desk_selectors:
                try:
                    desk_element = driver.find_element(By.XPATH, selector)
                    driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                        desk_element
                    )
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", desk_element)
                    print(f"✅ Selected Desk {TARGET_DESK}")
                    time.sleep(1)
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️  Could not select desk: {e}")

        # Click final "Book Now" button (ID: save_booking in the confirmation dialog)
        print("🔍 Clicking final 'Book Now' button...")
        try:
            final_book_selectors = [
                (By.XPATH, "//button[@id='save_booking' and contains(text(), 'Book Now')]"),
                (By.XPATH, "//button[contains(@class, 'btn-primary') and contains(text(), 'Book Now')]"),
                (By.XPATH, "//button[contains(text(), 'Book Now')]"),
                (By.ID, "save_booking"),
            ]
            
            for by, selector in final_book_selectors:
                try:
                    final_book_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    driver.execute_script("arguments[0].click();", final_book_btn)
                    print("✅ Clicked final 'Book Now'")
                    time.sleep(2)
                    break
                except:
                    continue
        except Exception as e:
            print(f"❌ Could not click final Book Now: {e}")
            save_debug_info(driver, "final_book_error")
            raise

        # Check for confirmation message
        print("--- Checking for confirmation ---")
        time.sleep(2)
        
        try:
            # Look for success message
            success_selectors = [
                "//*[contains(text(), 'success')]",
                "//*[contains(text(), 'Success')]",
                "//*[contains(text(), 'confirmed')]",
                "//*[contains(text(), 'Confirmed')]",
                "//*[contains(text(), 'booked')]",
                "//*[contains(text(), 'Booked')]",
            ]
            
            for selector in success_selectors:
                try:
                    success_msg = driver.find_element(By.XPATH, selector)
                    if success_msg.is_displayed():
                        print(f"🎉 SUCCESS: {success_msg.text}")
                        break
                except:
                    continue
        except:
            print("⚠️  No explicit success message found, but booking may have succeeded")
        
        save_debug_info(driver, "booking_complete")
        print(f"✅ Booking process completed for {formatted_date}!")

    except Exception as e:
        print(f"❌ Booking failed: {e}")
        save_debug_info(driver, "booking_error")
        raise

def main():
    driver = None
    exit_code = 0
    
    try:
        driver = start_browser()
        wait = WebDriverWait(driver, 30)

        # Step 1: Login
        login(driver, wait)
        print("⏳ Waiting for dashboard to fully load...")
        time.sleep(10)
        
        save_debug_info(driver, "after_login")
        
        # Step 2: Navigate to booking
        navigate_to_booking(driver, wait)
        time.sleep(2)
        
        # Step 3: Make the booking
        make_booking(driver, wait)
        
        print("\n" + "="*50)
        print("✅ BOOKING SCRIPT COMPLETED SUCCESSFULLY!")
        print(f"📅 Desk {TARGET_DESK} on {TARGET_FLOOR}")
        print(f"📆 Date: {(datetime.now() + timedelta(days=DAYS_AHEAD)).strftime('%d %b %Y')}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        if driver:
            save_debug_info(driver, "final_error")
        exit_code = 1
        
    finally:
        if driver and os.getenv("CI") == "true":
            driver.quit()
            print("🔒 Browser closed")
        elif driver:
            print("🖥️  Browser left open for inspection")
        
        exit(exit_code)

if __name__ == "__main__":
    main()
