import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# ================= CONFIGURATION =================
# HARDCODE YOUR CREDENTIALS HERE
EMAIL = "srinivasareddy.kumbagiri@juliusbaer.com"  # CHANGE THIS
PASSWORD = "Forgot@123"  # CHANGE THIS
BUILDING = "ONE@CHANGI CITY"
LEVEL = "06"
TARGET_DESK = "177"  # Specific desk to book
DAYS_AHEAD = 4  # Book 4th day from today
# ================================================

def calculate_target_date():
    """Calculate the target date (4th day from today)"""
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=DAYS_AHEAD)
    
    # Skip weekends if needed (optional)
    while target_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        target_date += datetime.timedelta(days=1)
    
    return target_date

def select_specific_date(driver, target_date):
    """Select specific date from calendar"""
    try:
        print(f"📅 Selecting date: {target_date.strftime('%d %B %Y')}")
        
        # Click calendar icon
        calendar_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'calendar_icon')]"))
        )
        calendar_icon.click()
        print("   ✓ Opened calendar")
        time.sleep(2)
        
        # Get day, month, year
        day = target_date.day
        month = target_date.strftime('%B')  # Full month name
        year = target_date.year
        
        # Strategy 1: Try to navigate to correct month/year first
        try:
            # Look for month/year header
            month_year_element = driver.find_element(By.XPATH, "//th[@class='month']")
            current_month_year = month_year_element.text
            
            # If not correct month, navigate
            if month not in current_month_year:
                # Click next button until we find the right month
                next_buttons = driver.find_elements(By.XPATH, "//th[@class='next']")
                if next_buttons:
                    for _ in range(12):  # Max 12 months
                        next_buttons[0].click()
                        time.sleep(0.5)
                        current_month_year = month_year_element.text
                        if month in current_month_year:
                            break
        except:
            pass
        
        # Strategy 2: Look for the specific day
        day_elements = driver.find_elements(By.XPATH, f"//td[text()='{day}']")
        
        for day_element in day_elements:
            try:
                if day_element.is_displayed() and day_element.is_enabled():
                    # Check if it's not a disabled date (not in past month)
                    if 'disabled' not in day_element.get_attribute('class') and \
                       'old' not in day_element.get_attribute('class'):
                        day_element.click()
                        print(f"   ✓ Selected day {day}")
                        return True
            except:
                continue
        
        # Strategy 3: Try with data-date attribute
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            date_element = driver.find_element(By.XPATH, f"//td[@data-date='{date_str}']")
            date_element.click()
            print(f"   ✓ Selected date via data-date attribute")
            return True
        except:
            pass
        
        print(f"   ⚠ Could not auto-select date {day}. Please select manually.")
        time.sleep(5)  # Give time for manual selection
        return True
        
    except Exception as e:
        print(f"   ❌ Date selection error: {str(e)}")
        driver.save_screenshot("date_selection_error.png")
        return False

def select_specific_desk(driver, desk_number):
    """Select specific desk by number"""
    try:
        print(f"🪑 Looking for desk {desk_number}...")
        
        # First, wait for the floor plan to load
        time.sleep(3)
        
        # Strategy 1: Look for desk by its number in the SVG/text
        # Desk numbers might be in text elements
        try:
            # Look for text elements containing the desk number
            desk_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{desk_number}')]")
            
            for desk_element in desk_elements:
                try:
                    if desk_element.is_displayed():
                        # Click near the desk (might need to use ActionChains)
                        actions = ActionChains(driver)
                        actions.move_to_element(desk_element).click().perform()
                        print(f"   ✓ Clicked desk {desk_number} via text")
                        time.sleep(2)
                        return True
                except:
                    continue
        except:
            pass
        
        # Strategy 2: Look for desk markers and check their tooltips/attributes
        try:
            # Find all desk markers
            desk_markers = driver.find_elements(By.XPATH, "//img[contains(@src, 'entitySelectedDwg.svg')]")
            
            for marker in desk_markers:
                try:
                    # Get parent element which might contain desk info
                    parent = marker.find_element(By.XPATH, "./..")
                    
                    # Check if desk number is in title, alt, or any attribute
                    title = marker.get_attribute('title') or ''
                    alt = marker.get_attribute('alt') or ''
                    outer_html = marker.get_attribute('outerHTML') or ''
                    
                    if desk_number in title or desk_number in alt or desk_number in outer_html:
                        marker.click()
                        print(f"   ✓ Found desk {desk_number} via marker attributes")
                        time.sleep(2)
                        return True
                except:
                    continue
        except:
            pass
        
        # Strategy 3: Try to find by coordinates or specific patterns
        print(f"   ⚠ Could not find desk {desk_number} automatically")
        print("   Please select desk manually from the map")
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"   ❌ Desk selection error: {str(e)}")
        driver.save_screenshot("desk_selection_error.png")
        return False

def book_desk():
    print("🚀 Starting Jumpree Desk Booking Automation...")
    
    # Calculate target date
    target_date = calculate_target_date()
    print(f"📅 Target Date: {target_date.strftime('%A, %d %B %Y')}")
    print(f"🪑 Target Desk: {TARGET_DESK}")
    print(f"🏢 Building: {BUILDING}")
    print(f"📏 Level: {LEVEL}")
    
    if EMAIL == "your.email@domain.com" or PASSWORD == "your_password_here":
        print("❌ Please edit the script and add your email and password!")
        print("Change lines 10 and 11 in the script")
        return
    
    # Setup Chrome
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')  # Remove to see browser
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        actions = ActionChains(driver)
        
        # STEP 1: Login
        print("\n1. Logging in...")
        driver.get("https://jumpree.smartenspaces.com/")
        time.sleep(3)
        
        # Enter email
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(EMAIL)
        print("   ✓ Email entered")
        
        # Click proceed
        proceed_btn = driver.find_element(By.ID, "submit_btn")
        proceed_btn.click()
        time.sleep(2)
        
        # Enter password
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys(PASSWORD)
        print("   ✓ Password entered")
        
        # Accept terms
        try:
            terms_checkbox = driver.find_element(By.CSS_SELECTOR, "#acceptTerms-input")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
                print("   ✓ Terms accepted")
        except:
            print("   ⚠ Terms checkbox not found")
        
        # Click login
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' Login ']")))
        login_btn.click()
        time.sleep(5)
        print("   ✓ Login attempt completed")
        
        # STEP 2: Navigate to booking
        print("\n2. Navigating to booking...")
        booking_link = wait.until(EC.element_to_be_clickable((By.ID, "amenity_booking")))
        booking_link.click()
        time.sleep(3)
        print("   ✓ On booking page")
        
        # STEP 3: Start new booking
        print("\n3. Starting new booking...")
        book_now_btn = wait.until(EC.element_to_be_clickable((By.ID, "book_now_amenity")))
        book_now_btn.click()
        time.sleep(3)
        print("   ✓ Booking form opened")
        
        # STEP 4: Select date (4th day from today)
        print("\n4. Selecting date...")
        if not select_specific_date(driver, target_date):
            print("   ⚠ Continuing with manual date selection...")
        
        # Click Next after date selection
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")))
            next_btn.click()
            time.sleep(3)
            print("   ✓ Proceeded to next step")
        except:
            print("   ⚠ Next button not found, continuing...")
        
        # STEP 5: Select building and level
        print("\n5. Selecting location...")
        time.sleep(3)
        
        # Verify building
        try:
            building_element = wait.until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{BUILDING}')]"))
            )
            print(f"   ✓ Building found: {BUILDING}")
        except:
            print(f"   ⚠ Building '{BUILDING}' not found")
        
        # Select level
        try:
            # Click dropdown
            dropdown = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'fa-angle-down')]"))
            )
            dropdown.click()
            time.sleep(1)
            
            # Select level
            level_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Level {LEVEL}')]"))
            )
            level_option.click()
            print(f"   ✓ Level {LEVEL} selected")
            time.sleep(3)
        except Exception as e:
            print(f"   ⚠ Level selection failed: {str(e)}")
        
        # STEP 6: Select specific desk (177)
        print(f"\n6. Selecting desk {TARGET_DESK}...")
        if not select_specific_desk(driver, TARGET_DESK):
            print("   ⚠ Could not select desk automatically")
        
        # Click Next to proceed to confirmation
        try:
            next_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
            for btn in next_buttons:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print("   ✓ Proceeded to confirmation")
                    time.sleep(3)
                    break
        except:
            print("   ⚠ Could not find Next button")
        
        # STEP 7: Final confirmation
        print("\n7. Confirming booking...")
        try:
            confirm_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "save_booking"))
            )
            confirm_btn.click()
            print("   ✓ Booking confirmed!")
            time.sleep(5)
            
            # Check for success
            page_text = driver.page_source.lower()
            success_keywords = ["success", "confirmed", "booked", "thank you", "reservation"]
            
            if any(keyword in page_text for keyword in success_keywords):
                print("   ✅ BOOKING SUCCESSFUL!")
                
                # Save booking details
                booking_details = {
                    "date": target_date.strftime("%Y-%m-%d"),
                    "desk": TARGET_DESK,
                    "building": BUILDING,
                    "level": LEVEL,
                    "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open("booking_confirmation.txt", "w") as f:
                    for key, value in booking_details.items():
                        f.write(f"{key}: {value}\n")
                
                print("   📝 Booking details saved to booking_confirmation.txt")
            else:
                print("   ⚠ Booking status uncertain")
                
        except Exception as e:
            print(f"   ❌ Final confirmation failed: {str(e)}")
        
        print("\n" + "="*50)
        print("📋 BOOKING SUMMARY:")
        print("="*50)
        print(f"Date: {target_date.strftime('%A, %d %B %Y')}")
        print(f"Desk: {TARGET_DESK}")
        print(f"Building: {BUILDING}")
        print(f"Level: {LEVEL}")
        print("="*50)
        
        # Keep browser open for inspection
        print("\n⏳ Browser will stay open for 120 seconds...")
        time.sleep(120)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Save error screenshot
        if driver:
            driver.save_screenshot("booking_error.png")
            print("Error screenshot saved: booking_error.png")
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")

def main():
    print("="*60)
    print("JUMPREE DESK BOOKER - BOOKING DESK 177")
    print(f"Booking 4th day from today: {datetime.date.today().strftime('%d %B %Y')}")
    print("="*60)
    
    # Show booking schedule
    today = datetime.date.today()
    for i in range(1, 8):
        date = today + datetime.timedelta(days=i)
        day_marker = "→" if i == DAYS_AHEAD else " "
        print(f"{day_marker} Day {i}: {date.strftime('%A, %d %B %Y')}")
    
    print("\n" + "="*60)
    
    # Confirm booking
    target_date = calculate_target_date()
    print(f"\nWill book: Desk {TARGET_DESK} on {target_date.strftime('%A, %d %B %Y')}")
    print(f"Building: {BUILDING}, Level: {LEVEL}")
    
    if EMAIL == "your.email@domain.com":
        print("\n❌ PLEASE EDIT THE SCRIPT FIRST!")
        print("Change lines 10-11 with your actual credentials")
        return
    
    print("\nStarting in 5 seconds...")
    time.sleep(5)
    
    # Start booking
    book_desk()

if __name__ == "__main__":
    main()
