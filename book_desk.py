import os
import sys
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess

# ================= CONFIGURATION =================
# Get from environment variables (safer) or hardcode
EMAIL = os.getenv('JUMPREE_EMAIL', 'srinivasareddy.kumbagiri@juliusbaer.com')
PASSWORD = os.getenv('JUMPREE_PASSWORD', 'Forgot@123')
BUILDING = "ONE@CHANGI CITY"
LEVEL = "06"
DESK_NUMBER = "177"
DAYS_AHEAD = 3  # Book 4th day from today
# ================================================

def setup_chrome():
    """Setup Chrome with proper configuration for CI/CD environments"""
    chrome_options = Options()
    
    # Essential arguments for CI/CD
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # Required for CI
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    # Additional stability options
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--safebrowsing-disable-auto-update')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    
    # Experimental options
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Try different approaches to start Chrome
    try:
        print("Attempt 1: Trying with ChromeDriverManager...")
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e1:
        print(f"Attempt 1 failed: {e1}")
        
        try:
            print("Attempt 2: Trying with direct ChromeDriver...")
            # For GitHub Actions, Chrome is usually at /usr/bin/google-chrome
            chrome_options.binary_location = '/usr/bin/google-chrome'
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e2:
            print(f"Attempt 2 failed: {e2}")
            
            try:
                print("Attempt 3: Trying alternative approach...")
                # Use ChromeDriver from PATH
                driver = webdriver.Chrome(
                    executable_path='/usr/local/bin/chromedriver',
                    options=chrome_options
                )
                return driver
            except Exception as e3:
                print(f"Attempt 3 failed: {e3}")
                raise Exception(f"All Chrome startup attempts failed: {e1}, {e2}, {e3}")

def check_chrome_installation():
    """Check if Chrome is properly installed"""
    print("Checking Chrome installation...")
    
    # Check Chrome version
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Chrome found: {result.stdout.strip()}")
        else:
            print(f"✗ Chrome check failed: {result.stderr}")
    except Exception as e:
        print(f"✗ Chrome check error: {e}")
    
    # Check ChromeDriver
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ ChromeDriver found: {result.stdout.strip()}")
        else:
            print(f"✗ ChromeDriver check failed: {result.stderr}")
    except Exception as e:
        print(f"✗ ChromeDriver check error: {e}")

def calculate_target_date():
    """Calculate the target date (4th day from today)"""
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=DAYS_AHEAD)
    
    # Skip weekends if needed
    while target_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        target_date += datetime.timedelta(days=1)
        print(f"  Skipped weekend, new target: {target_date.strftime('%A')}")
    
    return target_date

def simple_booking_flow():
    """Simplified booking flow for CI/CD"""
    print("=" * 60)
    print("JUMPREE DESK BOOKING AUTOMATION")
    print(f"Target: Desk {DESK_NUMBER}, {DAYS_AHEAD} days from today")
    print("=" * 60)
    
    # Check credentials
    if EMAIL == 'your.email@domain.com' or PASSWORD == 'your_password_here':
        print("❌ ERROR: Please set JUMPREE_EMAIL and JUMPREE_PASSWORD environment variables")
        print("OR edit the script with your credentials")
        return False
    
    # Check Chrome installation
    check_chrome_installation()
    
    driver = None
    try:
        # Setup Chrome
        print("\n1. Setting up Chrome driver...")
        driver = setup_chrome()
        print("✓ Chrome driver initialized successfully")
        
        # Set longer timeout
        wait = WebDriverWait(driver, 30)
        
        # Calculate target date
        target_date = calculate_target_date()
        print(f"\n📅 Booking for: {target_date.strftime('%A, %B %d, %Y')}")
        
        # STEP 1: Login
        print("\n2. Logging in...")
        driver.get("https://jumpree.smartenspaces.com/")
        time.sleep(5)
        
        # Save initial page
        driver.save_screenshot("01_initial_page.png")
        print("✓ Page loaded, screenshot saved")
        
        # Find and fill email
        try:
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(EMAIL)
            print("✓ Email entered")
            
            # Click proceed
            proceed_btn = driver.find_element(By.ID, "submit_btn")
            proceed_btn.click()
            time.sleep(3)
            
            driver.save_screenshot("02_email_submitted.png")
        except Exception as e:
            print(f"✗ Email step failed: {e}")
            return False
        
        # Find and fill password
        try:
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(PASSWORD)
            print("✓ Password entered")
            
            # Accept terms if exists
            try:
                terms = driver.find_element(By.CSS_SELECTOR, "#acceptTerms-input")
                if not terms.is_selected():
                    terms.click()
                    print("✓ Terms accepted")
            except:
                pass
            
            # Click login
            login_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login')]")
            for btn in login_btns:
                if btn.is_displayed():
                    btn.click()
                    break
            print("✓ Login clicked")
            
            time.sleep(5)
            driver.save_screenshot("03_login_attempt.png")
            
        except Exception as e:
            print(f"✗ Password/login step failed: {e}")
            return False
        
        # Check login success
        if "login" not in driver.current_url.lower():
            print("✓ Login appears successful")
        else:
            print("⚠ Still on login page, but continuing...")
        
        # STEP 2: Navigate to booking
        print("\n3. Navigating to booking...")
        try:
            booking_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'booking') or contains(@href, 'amenity')]")
            if booking_links:
                booking_links[0].click()
                print("✓ Clicked booking link")
                time.sleep(3)
                driver.save_screenshot("04_booking_page.png")
        except:
            print("⚠ Could not find booking link, trying manual navigation...")
            # Try to go directly
            driver.get("https://jumpree.smartenspaces.com/#/layout/amenity-booking")
            time.sleep(3)
        
        # STEP 3: Start booking
        print("\n4. Starting booking process...")
        try:
            book_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Book')]")
            for btn in book_buttons:
                if btn.is_displayed():
                    btn.click()
                    print("✓ Clicked Book button")
                    time.sleep(3)
                    break
        except:
            print("⚠ Could not find Book button")
        
        driver.save_screenshot("05_booking_started.png")
        
        # At this point, we've reached the booking form
        print("\n✅ Basic automation completed!")
        print("\nFrom here, you would:")
        print(f"1. Select date: {target_date.strftime('%B %d')}")
        print(f"2. Choose building: {BUILDING}")
        print(f"3. Select level: {LEVEL}")
        print(f"4. Find and select desk: {DESK_NUMBER}")
        print("5. Confirm booking")
        
        # Save page source for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n📄 Page source saved to: page_source.html")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Save error page
        if driver:
            try:
                driver.save_screenshot("error_final.png")
                with open("error_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("Error screenshots saved")
            except:
                pass
        return False
        
    finally:
        if driver:
            print("\n5. Closing browser...")
            try:
                driver.quit()
                print("✓ Browser closed")
            except:
                pass

if __name__ == "__main__":
    success = simple_booking_flow()
    if success:
        print("\n" + "=" * 60)
        print("✅ SCRIPT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ SCRIPT FAILED!")
        print("=" * 60)
        sys.exit(1)
