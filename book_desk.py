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
DAYS_AHEAD = 4  # Book 4 days in advance
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

def login(driver, wait):
    """Handle login flow"""
    print("--- Navigating to Login ---")
    driver.get(URL)
    time.sleep(3)  # Let page load

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
            print("⚠️  No checkbox found (may not be required)")

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
    """Navigate: Booking menu → Book Now button (JavaScript click version)"""
    print("--- Navigating to Booking ---")
    
    # STEP 1: Click "Booking" menu using ID
    print("🔍 Step 1: Clicking 'Booking' menu...")
    
    booking_menu_selectors = [
        (By.ID, "amenity_booking"),
        (By.XPATH, "//a[@id='amenity_booking']"),
        (By.XPATH, "//a[@href='#/layout/amenity-booking']"),
        (By.XPATH, "//a[@routerlink='amenity-booking']"),
        (By.XPATH, "//a[contains(@class, 'nav-link')]//span[text()='Booking']/.."),
    ]
    
    booking_clicked = False
    for i, (by, selector) in enumerate(booking_menu_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(booking_menu_selectors)}...")
            booking_menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", booking_menu)
            time.sleep(0.5)
            
            # Click via JavaScript (more reliable in headless)
            driver.execute_script("arguments[0].click();", booking_menu)
            print(f"✅ Clicked 'Booking' menu (selector {i})")
            booking_clicked = True
            time.sleep(3)  # Wait for page transition
            break
        except TimeoutException:
            continue
        except Exception as e:
            print(f"  ⚠️  Selector {i} failed: {e}")
            continue
    
    if not booking_clicked:
        print("❌ Could not click 'Booking' menu")
        save_debug_info(driver, "booking_menu_not_found")
        
        # Debug: Show available navigation items
        print("\n📋 Available navigation items:")
        try:
            nav_items = driver.find_elements(By.XPATH, "//a[contains(@class, 'nav-link')]")
            for item in nav_items:
                text = item.text.strip()
                item_id = item.get_attribute('id')
                href = item.get_attribute('href')
                print(f"  - Text: '{text}' | ID: '{item_id}' | Href: '{href}'")
        except:
            pass
        
        raise Exception("Could not find 'Booking' menu item")
    
    # Verify we're on the booking page
    try:
        WebDriverWait(driver, 5).until(
            lambda d: "amenity-booking" in d.current_url or "booking" in d.current_url.lower()
        )
        print(f"✅ Navigated to booking page: {driver.current_url}")
    except:
        print(f"⚠️  URL didn't change as expected. Current: {driver.current_url}")
    
    # STEP 2: Click "Book Now" button
    print("🔍 Step 2: Looking for 'Book Now' button...")
    
    book_now_selectors = [
        "//button[contains(text(), 'Book Now')]",
        "//a[contains(text(), 'Book Now')]",
        "//button[contains(., 'Book Now')]",
        "//div[contains(text(),'Desks')]/..//button[contains(text(), 'Book Now')]",
        "//div[contains(text(),'Desk')]//following::button[contains(text(), 'Book Now')][1]",
        "//*[contains(text(), 'Book Now') and (self::button or self::a)]",
        "//button[normalize-space()='Book Now']",
        "//*[contains(@class, 'book') and contains(text(), 'Now')]",
    ]
    
    for i, selector in enumerate(book_now_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(book_now_selectors)}...")
            book_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", book_btn)
            time.sleep(0.5)
            
            # Click via JavaScript
            driver.execute_script("arguments[0].click();", book_btn)
            print(f"✅ Clicked 'Book Now' button (selector {i})")
            time.sleep(2)
            return
        except TimeoutException:
            continue
        except Exception as e:
            print(f"  ⚠️  Selector {i} failed: {e}")
            continue
    
    print("❌ Could not find 'Book Now' button")
    save_debug_info(driver, "book_now_not_found")
    
    # Debug: Show available buttons
    print("\n📋 Available buttons on page:")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons[:20]:
            text = btn.text.strip()
            if text:
                classes = btn.get_attribute('class')
                print(f"  - '{text}' | Classes: {classes}")
    except:
        pass
    
    print("\n📋 Available links on page:")
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links[:20]:
            text = link.text.strip()
            if text:
                href = link.get_attribute('href')
                print(f"  - '{text}' | Href: {href}")
    except:
        pass
    
    raise Exception("Could not find 'Book Now' button")

def make_booking(driver, wait):
    """Complete the booking process"""
    print("--- Setting up Booking Details ---")

    try:
        # Save state before attempting booking
        save_debug_info(driver, "before_booking")
        
        # 1. Calculate target date
        target_date = datetime.now() + timedelta(days=DAYS_AHEAD)
        formatted_date = target_date.strftime("%d %b %Y")  # e.g., "29 Jan 2025"
        print(f"📅 Target Date: {formatted_date}")

        # 2. Select Floor (if needed)
        try:
            floor_selector = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{TARGET_FLOOR}')]"))
            )
            driver.execute_script("arguments[0].click();", floor_selector)
            print(f"✅ Floor selected: {TARGET_FLOOR}")
        except Exception as e:
            print(f"⚠️  Could not select floor (may already be set): {e}")

        # 3. Set Date
        try:
            date_picker = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Date'], input[type='date']"))
            )
            date_picker.clear()
            date_picker.send_keys(formatted_date)
            date_picker.send_keys(Keys.RETURN)
            time.sleep(2)
            print(f"✅ Date set: {formatted_date}")
        except Exception as e:
            print(f"⚠️  Date picker issue: {e}")

        # 4. Set Time (uncomment and adjust selectors as needed)
        """
        print(f"--- Setting Time: {START_TIME} to {END_TIME} ---")
        try:
            start_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[1]")
            start_time_dropdown.click()
            select_start = driver.find_element(By.XPATH, f"//span[contains(text(), '{START_TIME}')]")
            driver.execute_script("arguments[0].click();", select_start)

            end_time_dropdown = driver.find_element(By.XPATH, "(//input[@role='combobox'])[2]")
            end_time_dropdown.click()
            select_end = driver.find_element(By.XPATH, f"//span[contains(text(), '{END_TIME}')]")
            driver.execute_script("arguments[0].click();", select_end)
            print("✅ Time set")
        except Exception as e:
            print(f"⚠️  Time selection failed: {e}")
        """

        # 5. Click Next/Search
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Search')]")
                )
            )
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            print("✅ Clicked Next")
        except Exception as e:
            print(f"⚠️  No Next button found: {e}")

        # 6. Select Desk 177
        print(f"--- Searching for Desk {TARGET_DESK} ---")
        
        # Try switching to List View first
        try:
            list_view_selectors = [
                ".fa-list",
                ".icon-list",
                "button[title='List View']",
                "//*[contains(@class, 'list')]",
                "//button[contains(., 'List')]",
            ]
            
            for selector in list_view_selectors:
                try:
                    if selector.startswith("//"):
                        list_view_btn = driver.find_element(By.XPATH, selector)
                    else:
                        list_view_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    driver.execute_script("arguments[0].click();", list_view_btn)
                    time.sleep(1)
                    print("✅ Switched to List View")
                    break
                except:
                    continue
        except:
            print("⚠️  List view button not found, continuing...")

        # Search for desk
        try:
            search_box = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
            )
            search_box.clear()
            search_box.send_keys(TARGET_DESK)
            time.sleep(2)
            print(f"✅ Searched for desk: {TARGET_DESK}")
        except Exception as e:
            print(f"⚠️  Search box not found: {e}")

        # Book the desk
        try:
            book_desk_selectors = [
                f"//div[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]",
                f"//td[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]",
                f"//*[contains(text(), '{TARGET_DESK}')]/ancestor::tr//button[contains(text(), 'Book')]",
                f"//*[contains(text(), '{TARGET_DESK}')]/following::button[contains(text(), 'Book')][1]",
            ]
            
            book_desk_btn = None
            for selector in book_desk_selectors:
                try:
                    book_desk_btn = driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if book_desk_btn:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", book_desk_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", book_desk_btn)
                print(f"✅ Clicked Book for Desk {TARGET_DESK}")
            else:
                raise Exception(f"Could not find Book button for desk {TARGET_DESK}")
                
        except Exception as e:
            print(f"❌ Could not find/book desk: {e}")
            save_debug_info(driver, "desk_selection_error")
            raise

        # 7. Final Confirmation
        print("--- Confirming Booking ---")
        try:
            confirm_selectors = [
                "//button[contains(text(), 'Confirm')]",
                "//button[contains(text(), 'Yes')]",
                "//button[contains(., 'Confirm')]",
                "//button[@type='submit']",
            ]
            
            confirm_btn = None
            for selector in confirm_selectors:
                try:
                    confirm_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if confirm_btn:
                driver.execute_script("arguments[0].click();", confirm_btn)
                time.sleep(2)
                print(f"🎉 SUCCESS: Booking Confirmed for {formatted_date}!")
            else:
                raise Exception("Could not find Confirm button")
                
        except Exception as e:
            print(f"❌ Confirmation failed: {e}")
            save_debug_info(driver, "confirmation_error")
            raise

    except Exception as e:
        print(f"❌ Booking process failed: {e}")
        save_debug_info(driver, "booking_error")
        raise

def main():
    driver = None
    exit_code = 0
    
    try:
        driver = start_browser()
        wait = WebDriverWait(driver, 20)

        # Step 1: Login
        login(driver, wait)
        print("⏳ Waiting for dashboard to load...")
        time.sleep(8)  # Increased wait time for SPA
        
        save_debug_info(driver, "after_login")
        
        # Step 2: Navigate to booking
        navigate_to_booking(driver, wait)
        time.sleep(3)
        
        # Step 3: Make the booking
        make_booking(driver, wait)
        
        print("\n✅ Script completed successfully!")
        print(f"📅 Desk {TARGET_DESK} booked for {(datetime.now() + timedelta(days=DAYS_AHEAD)).strftime('%d %b %Y')}")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        if driver:
            save_debug_info(driver, "final_error")
        print("📸 Debug screenshots and HTML saved")
        exit_code = 1
        
    finally:
        # Only close in CI mode
        if driver and os.getenv("CI") == "true":
            driver.quit()
            print("🔒 Browser closed")
        elif driver:
            print("🖥️  Browser left open for inspection")
        
        exit(exit_code)

if __name__ == "__main__":
    main()
