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
    
    wait = WebDriverWait(driver, timeout)
    
    # Wait for Angular to be defined
    try:
        wait.until(lambda d: d.execute_script(
            "return typeof angular !== 'undefined' || "
            "typeof getAllAngularRootElements !== 'undefined' || "
            "document.readyState === 'complete'"
        ))
        print("✅ Angular detected or page ready")
    except:
        print("⚠️  Angular not detected, but continuing...")
    
    # Wait for any loading spinners to disappear
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 
            ".spinner, .loading, .loader, [class*='spin'], [class*='load']"
        )))
        print("✅ Loading spinners cleared")
    except:
        print("⚠️  No spinners found or still visible")
    
    # Additional wait for network idle (simulate)
    time.sleep(2)
    
    # Execute Angular-specific wait if available
    try:
        driver.execute_script("""
            if (window.angular) {
                var injector = angular.element(document.body).injector();
                if (injector) {
                    var $browser = injector.get('$browser');
                    $browser.notifyWhenNoOutstandingRequests(function(){});
                }
            }
        """)
        print("✅ Angular requests completed")
    except:
        pass

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
    """Navigate: Booking menu → Book Now button"""
    print("--- Navigating to Booking ---")
    
    # Wait for Angular and navigation to be ready
    wait_for_angular(driver)
    
    # Additional explicit wait for navigation menu to be present
    print("🔍 Waiting for navigation menu to appear...")
    try:
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, 
            "a.nav-link, .nav-link, [class*='nav'], nav a"
        )))
        print("✅ Navigation menu detected")
    except:
        print("⚠️  Navigation menu not detected with CSS, trying XPath...")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//a | //nav")))
            print("✅ Some navigation elements found")
        except:
            print("❌ No navigation elements found at all")
            save_debug_info(driver, "no_navigation")
    
    time.sleep(3)  # Extra buffer for Angular rendering
    
    # STEP 1: Click "Booking" menu
    print("🔍 Step 1: Looking for 'Booking' menu...")
    
    booking_menu_selectors = [
        (By.ID, "amenity_booking"),
        (By.XPATH, "//a[@id='amenity_booking']"),
        (By.XPATH, "//a[contains(@href, 'amenity-booking')]"),
        (By.XPATH, "//a[contains(@routerlink, 'amenity-booking')]"),
        (By.XPATH, "//span[text()='Booking']/parent::a"),
        (By.XPATH, "//span[contains(text(), 'Booking')]/parent::a"),
        (By.XPATH, "//a[contains(@class, 'nav-link')]//span[text()='Booking']/.."),
        (By.XPATH, "//a[.//span[text()='Booking']]"),
        (By.XPATH, "//a[contains(., 'Booking')]"),
    ]
    
    booking_clicked = False
    for i, (by, selector) in enumerate(booking_menu_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(booking_menu_selectors)}: {by}...")
            
            # Use longer timeout for first selector
            timeout = 10 if i == 1 else 3
            booking_menu = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Check if element is visible
            is_visible = booking_menu.is_displayed()
            print(f"  Element found, visible: {is_visible}")
            
            # Scroll into view
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                booking_menu
            )
            time.sleep(1)
            
            # Highlight element (for debugging)
            driver.execute_script(
                "arguments[0].style.border='3px solid red'", 
                booking_menu
            )
            time.sleep(0.5)
            
            # Click via JavaScript
            driver.execute_script("arguments[0].click();", booking_menu)
            print(f"✅ Clicked 'Booking' menu (selector {i})")
            booking_clicked = True
            time.sleep(3)
            break
            
        except TimeoutException:
            print(f"  Selector {i} timed out")
            continue
        except Exception as e:
            print(f"  Selector {i} error: {str(e)[:100]}")
            continue
    
    if not booking_clicked:
        print("❌ Could not click 'Booking' menu")
        save_debug_info(driver, "booking_menu_not_found")
        
        # Enhanced debugging
        print("\n📋 Page body classes:")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            print(f"  {body.get_attribute('class')}")
        except:
            pass
        
        print("\n📋 All links on page:")
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"  Total links found: {len(all_links)}")
            for link in all_links[:30]:
                text = link.text.strip()
                href = link.get_attribute('href')
                link_id = link.get_attribute('id')
                classes = link.get_attribute('class')
                if text or href:
                    print(f"  - Text: '{text}' | ID: '{link_id}' | Class: '{classes}' | Href: '{href}'")
        except Exception as e:
            print(f"  Error listing links: {e}")
        
        print("\n📋 Navigation elements:")
        try:
            nav_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'nav')]")
            print(f"  Total nav elements found: {len(nav_elements)}")
            for nav in nav_elements[:10]:
                print(f"  - Tag: {nav.tag_name} | Class: {nav.get_attribute('class')}")
        except:
            pass
        
        raise Exception("Could not find 'Booking' menu item")
    
    # Verify navigation
    try:
        WebDriverWait(driver, 5).until(
            lambda d: "amenity-booking" in d.current_url or "booking" in d.current_url.lower()
        )
        print(f"✅ Navigated to booking page: {driver.current_url}")
    except:
        print(f"⚠️  URL: {driver.current_url}")
        save_debug_info(driver, "after_booking_click")
    
    # Wait for page to load
    wait_for_angular(driver)
    
    # STEP 2: Click "Book Now" button
    print("🔍 Step 2: Looking for 'Book Now' button...")
    
    book_now_selectors = [
        "//button[contains(text(), 'Book Now')]",
        "//a[contains(text(), 'Book Now')]",
        "//button[normalize-space()='Book Now']",
        "//button[contains(., 'Book Now')]",
        "//*[contains(text(), 'Book Now')]",
        "//div[contains(text(),'Desk')]//following::button[contains(text(), 'Book Now')][1]",
    ]
    
    for i, selector in enumerate(book_now_selectors, 1):
        try:
            print(f"  Trying selector {i}/{len(book_now_selectors)}...")
            book_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                book_btn
            )
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", book_btn)
            print(f"✅ Clicked 'Book Now' button")
            time.sleep(2)
            return
            
        except TimeoutException:
            continue
        except Exception as e:
            print(f"  Selector {i} error: {str(e)[:100]}")
            continue
    
    print("❌ Could not find 'Book Now' button")
    save_debug_info(driver, "book_now_not_found")
    
    # Show available buttons
    print("\n📋 Available buttons:")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"  Total buttons found: {len(buttons)}")
        for btn in buttons[:20]:
            text = btn.text.strip()
            if text:
                print(f"  - {text}")
    except:
        pass
    
    raise Exception("Could not find 'Book Now' button")

def make_booking(driver, wait):
    """Complete the booking process"""
    print("--- Setting up Booking Details ---")

    try:
        wait_for_angular(driver)
        save_debug_info(driver, "before_booking")
        
        target_date = datetime.now() + timedelta(days=DAYS_AHEAD)
        formatted_date = target_date.strftime("%d %b %Y")
        print(f"📅 Target Date: {formatted_date}")

        # Set Date
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

        # Click Next/Search
        try:
            next_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Search')]")
                )
            )
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            print("✅ Clicked Next")
        except:
            print("⚠️  No Next button")

        # Wait for results
        wait_for_angular(driver)

        # Select Desk
        print(f"--- Searching for Desk {TARGET_DESK} ---")
        
        # Try list view
        try:
            list_view_selectors = [".fa-list", ".icon-list", "button[title='List View']"]
            for selector in list_view_selectors:
                try:
                    list_view_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", list_view_btn)
                    time.sleep(1)
                    print("✅ Switched to List View")
                    break
                except:
                    continue
        except:
            print("⚠️  No list view toggle")

        # Search
        try:
            search_box = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
            )
            search_box.clear()
            search_box.send_keys(TARGET_DESK)
            time.sleep(2)
            print(f"✅ Searched: {TARGET_DESK}")
        except Exception as e:
            print(f"⚠️  Search failed: {e}")

        # Book desk
        book_desk_selectors = [
            f"//div[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]",
            f"//td[contains(text(), '{TARGET_DESK}')]/..//button[contains(text(), 'Book')]",
            f"//*[contains(text(), '{TARGET_DESK}')]/ancestor::tr//button[contains(text(), 'Book')]",
        ]
        
        for selector in book_desk_selectors:
            try:
                book_desk_btn = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].click();", book_desk_btn)
                print(f"✅ Booked Desk {TARGET_DESK}")
                break
            except:
                continue
        else:
            raise Exception(f"Could not book desk {TARGET_DESK}")

        # Confirm
        print("--- Confirming Booking ---")
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)
        time.sleep(2)
        print(f"🎉 SUCCESS!")

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

        login(driver, wait)
        print("⏳ Waiting for dashboard...")
        time.sleep(10)  # Increased initial wait
        
        save_debug_info(driver, "after_login")
        
        navigate_to_booking(driver, wait)
        time.sleep(3)
        
        make_booking(driver, wait)
        
        print("\n✅ Booking completed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if driver:
            save_debug_info(driver, "final_error")
        exit_code = 1
        
    finally:
        if driver and os.getenv("CI") == "true":
            driver.quit()
            print("🔒 Browser closed")
        elif driver:
            print("🖥️  Browser left open")
        
        exit(exit_code)

if __name__ == "__main__":
    main()
