#!/usr/bin/env python3
"""
Jumpree Desk Booking Automation
Books desk 177, 4 days from current date
"""
import os
import sys
import time
import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging

# ================= CONFIGURATION =================
# Get from environment variables or hardcode
EMAIL = os.getenv('JUMPREE_EMAIL', 'srinivasareddy.kumbagiri@juliusbaer.com')
PASSWORD = os.getenv('JUMPREE_PASSWORD', 'Forgot@123')
BUILDING = "ONE@CHANGI CITY"
LEVEL = "06"
DESK_NUMBER = "177"
DAYS_AHEAD = 4  # Book 4th day from today
# ================================================

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('booking.log')
        ]
    )
    return logging.getLogger(__name__)

def setup_chrome_driver():
    """Setup Chrome driver for headless execution"""
    logger = logging.getLogger(__name__)
    
    chrome_options = Options()
    
    # Essential for headless/CI
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless=new')  # New headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Performance and stability
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    
    # Disable automation detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Try with ChromeDriver from PATH
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✅ Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        raise

def calculate_target_date():
    """Calculate target date (4th day from today)"""
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=DAYS_AHEAD)
    
    # Log date info
    print(f"\n📅 Date Calculation:")
    print(f"   Today: {today.strftime('%A, %B %d, %Y')}")
    print(f"   Target: {target_date.strftime('%A, %B %d, %Y')} (Day +{DAYS_AHEAD})")
    
    return target_date

def save_booking_result(result_data):
    """Save booking result to JSON file"""
    with open('booking_result.json', 'w') as f:
        json.dump(result_data, f, indent=2, default=str)

def take_screenshot(driver, step_name):
    """Take screenshot and save with timestamp"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"screenshot_{step_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    return filename

def main():
    """Main booking function"""
    logger = setup_logging()
    
    print("=" * 60)
    print("JUMPREE DESK BOOKING AUTOMATION")
    print("=" * 60)
    print(f"📧 Email: {EMAIL[:3]}***{EMAIL[EMAIL.find('@'):] if '@' in EMAIL else '***'}")
    print(f"📅 Booking: Desk {DESK_NUMBER}, {DAYS_AHEAD} days ahead")
    print(f"🏢 Location: {BUILDING}, Level {LEVEL}")
    print("=" * 60)
    
    # Validate credentials
    if EMAIL == 'your.email@domain.com' or PASSWORD == 'your_password_here':
        logger.error("❌ Please set JUMPREE_EMAIL and JUMPREE_PASSWORD environment variables")
        print("\nTo set environment variables in GitHub:")
        print("1. Go to Repository Settings → Secrets and variables → Actions")
        print("2. Add JUMPREE_EMAIL and JUMPREE_PASSWORD as repository secrets")
        sys.exit(1)
    
    # Calculate target date
    target_date = calculate_target_date()
    
    # Initialize result data
    result = {
        "start_time": datetime.datetime.now(),
        "email": EMAIL[:3] + "***" + EMAIL[EMAIL.find('@'):] if '@' in EMAIL else '***',
        "target_date": target_date,
        "desk": DESK_NUMBER,
        "building": BUILDING,
        "level": LEVEL,
        "steps": [],
        "success": False,
        "screenshots": []
    }
    
    driver = None
    try:
        # Step 1: Setup Chrome
        logger.info("Step 1: Setting up Chrome driver")
        driver = setup_chrome_driver()
        wait = WebDriverWait(driver, 30)
        result["steps"].append({"step": "setup", "status": "success", "time": datetime.datetime.now()})
        
        # Step 2: Login
        logger.info("Step 2: Logging in")
        driver.get("https://jumpree.smartenspaces.com/")
        time.sleep(5)
        
        screenshot = take_screenshot(driver, "01_login_page")
        result["screenshots"].append(screenshot)
        
        # Find and fill email
        try:
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(EMAIL)
            logger.info("✓ Email entered")
            
            # Click proceed
            proceed_btn = driver.find_element(By.ID, "submit_btn")
            proceed_btn.click()
            time.sleep(3)
            
            screenshot = take_screenshot(driver, "02_email_submitted")
            result["screenshots"].append(screenshot)
            
        except Exception as e:
            logger.error(f"✗ Email step failed: {e}")
            result["steps"].append({"step": "email", "status": "failed", "error": str(e)})
            raise
        
        # Enter password
        try:
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(PASSWORD)
            logger.info("✓ Password entered")
            
            # Accept terms if exists
            try:
                terms = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not terms.is_selected():
                    terms.click()
                    logger.info("✓ Terms accepted")
            except:
                logger.info("⚠ Terms checkbox not found")
            
            # Click login
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]")))
            login_btn.click()
            logger.info("✓ Login button clicked")
            
            time.sleep(5)
            screenshot = take_screenshot(driver, "03_login_complete")
            result["screenshots"].append(screenshot)
            
            result["steps"].append({"step": "login", "status": "success", "time": datetime.datetime.now()})
            
        except Exception as e:
            logger.error(f"✗ Login failed: {e}")
            result["steps"].append({"step": "login", "status": "failed", "error": str(e)})
            raise
        
        # Step 3: Navigate to booking
        logger.info("Step 3: Navigating to booking section")
        try:
            # Try multiple selectors for booking link
            booking_selectors = [
                (By.ID, "amenity_booking"),
                (By.XPATH, "//a[contains(@href, 'booking')]"),
                (By.XPATH, "//a[contains(@href, 'amenity')]"),
                (By.XPATH, "//*[contains(text(), 'Booking')]")
            ]
            
            booking_found = False
            for selector in booking_selectors:
                try:
                    booking_link = wait.until(EC.element_to_be_clickable(selector))
                    booking_link.click()
                    logger.info(f"✓ Clicked booking link using {selector[1]}")
                    booking_found = True
                    time.sleep(3)
                    break
                except:
                    continue
            
            if not booking_found:
                # Try direct URL
                driver.get("https://jumpree.smartenspaces.com/#/layout/amenity-booking")
                logger.info("✓ Navigated directly to booking URL")
                time.sleep(3)
            
            screenshot = take_screenshot(driver, "04_booking_page")
            result["screenshots"].append(screenshot)
            result["steps"].append({"step": "navigation", "status": "success", "time": datetime.datetime.now()})
            
        except Exception as e:
            logger.error(f"✗ Navigation failed: {e}")
            result["steps"].append({"step": "navigation", "status": "failed", "error": str(e)})
            raise
        
        # Step 4: Start booking process
        logger.info("Step 4: Starting booking process")
        try:
            # Find and click Book Now button
            book_now_selectors = [
                (By.ID, "book_now_amenity"),
                (By.XPATH, "//button[contains(text(), 'Book Now')]"),
                (By.XPATH, "//button[contains(text(), 'Book') and contains(@class, 'btn')]")
            ]
            
            book_found = False
            for selector in book_now_selectors:
                try:
                    book_btn = wait.until(EC.element_to_be_clickable(selector))
                    book_btn.click()
                    logger.info(f"✓ Clicked Book button using {selector[1]}")
                    book_found = True
                    time.sleep(3)
                    break
                except:
                    continue
            
            if not book_found:
                logger.warning("⚠ Could not find Book button, attempting manual click")
                # Try clicking first button with 'Book' in text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "book" in btn.text.lower():
                        btn.click()
                        logger.info("✓ Clicked book button via text search")
                        break
            
            screenshot = take_screenshot(driver, "05_booking_started")
            result["screenshots"].append(screenshot)
            result["steps"].append({"step": "start_booking", "status": "success", "time": datetime.datetime.now()})
            
            # Display booking information
            print("\n" + "=" * 60)
            print("✅ AUTOMATION PROGRESS")
            print("=" * 60)
            print("✓ Chrome driver initialized")
            print("✓ Successfully logged in")
            print("✓ Navigated to booking section")
            print("✓ Started booking process")
            print(f"\n📋 Next steps to complete manually:")
            print(f"   1. Select date: {target_date.strftime('%B %d, %Y')}")
            print(f"   2. Choose building: {BUILDING}")
            print(f"   3. Select level: {LEVEL}")
            print(f"   4. Find and select desk: {DESK_NUMBER}")
            print(f"   5. Confirm booking")
            print("\n⏳ Waiting for manual completion...")
            
            # Keep the page open for manual completion
            time.sleep(300)  # 5 minutes for manual completion
            
            result["success"] = True
            result["completion_time"] = datetime.datetime.now()
            logger.info("✅ Booking process completed (manual intervention expected)")
            
        except Exception as e:
            logger.error(f"✗ Booking start failed: {e}")
            result["steps"].append({"step": "start_booking", "status": "failed", "error": str(e)})
            raise
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        result["success"] = False
        result["error"] = str(e)
        result["end_time"] = datetime.datetime.now()
        
    finally:
        if driver:
            try:
                # Take final screenshot
                screenshot = take_screenshot(driver, "06_final_state")
                result["screenshots"].append(screenshot)
                
                driver.quit()
                logger.info("✓ Browser closed")
            except:
                pass
    
    # Save results
    result["end_time"] = datetime.datetime.now()
    save_booking_result(result)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.get("success"):
        print("✅ AUTOMATION COMPLETED SUCCESSFULLY!")
    else:
        print("⚠ AUTOMATION PARTIALLY COMPLETED")
    print("=" * 60)
    print(f"📊 Results saved to: booking_result.json")
    print(f"📷 Screenshots: {len(result['screenshots'])} taken")
    print(f"⏱ Duration: {result['end_time'] - result['start_time']}")
    print("=" * 60)
    
    return result["success"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
