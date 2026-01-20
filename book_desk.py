import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import sys

# ================= CONFIGURATION =================
# Get credentials from environment variables (safer) or hardcode
EMAIL = os.getenv('JUMPREE_EMAIL', 'srinivasareddy.kumbagiri@juliusbaer.com')  # Set in GitHub Secrets
PASSWORD = os.getenv('JUMPREE_PASSWORD', 'Forgot@123')  # Set in GitHub Secrets
BUILDING = "ONE@CHANGI CITY"
LEVEL = "06"
DAYS_AHEAD = 1
# ================================================

def setup_driver():
    """Setup Chrome driver for GitHub Actions"""
    chrome_options = Options()
    
    # GitHub Actions specific settings
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # Headless for CI
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    # Binary location for GitHub Actions
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    # Use ChromeDriverManager or specify path
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        # Fallback to direct path
        service = Service(executable_path='/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def simple_booking():
    print("🚀 Starting Jumpree Desk Booking...")
    print(f"📧 Email: {EMAIL[:3]}***@{EMAIL.split('@')[1] if '@' in EMAIL else '***'}")
    
    if EMAIL == 'your.email@domain.com' or PASSWORD == 'your_password_here':
        print("\n❌ ERROR: Please set JUMPREE_EMAIL and JUMPREE_PASSWORD environment variables")
        print("In GitHub: Settings → Secrets and variables → Actions → New repository secret")
        return False
    
    driver = None
    try:
        print("1. Setting up Chrome driver...")
        driver = setup_driver()
        wait = WebDriverWait(driver, 30)
        
        # Step 1: Login
        print("2. Logging in...")
        driver.get("https://jumpree.smartenspaces.com/")
        time.sleep(5)
        
        # Take screenshot for debugging
        driver.save_screenshot("step1_homepage.png")
        print("   Screenshot saved: step1_homepage.png")
        
        # Enter email
        try:
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(EMAIL)
            print("   ✓ Email entered")
            
            # Click proceed
            proceed_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit_btn")))
            proceed_btn.click()
            time.sleep(3)
            
            driver.save_screenshot("step2_email_sent.png")
        except Exception as e:
            print(f"   ✗ Email step failed: {str(e)}")
            driver.save_screenshot("error_email.png")
            return False
        
        # Enter password
        try:
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(PASSWORD)
            print("   ✓ Password entered")
            
            # Accept terms if exists
            try:
                terms = driver.find_element(By.CSS_SELECTOR, "#acceptTerms-input")
                if not terms.is_selected():
                    terms.click()
                    print("   ✓ Accepted terms")
            except:
                print("   ⚠ Terms checkbox not found")
            
            # Click login
            login_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login')]")
            login_clicked = False
            for btn in login_btns:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    login_clicked = True
                    print("   ✓ Login button clicked")
                    break
            
            if not login_clicked:
                # Try alternative selector
                login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_btn.click()
                print("   ✓ Submit button clicked")
            
            time.sleep(5)
            driver.save_screenshot("step3_logged_in.png")
            print("   ✓ Login attempt completed")
            
        except Exception as e:
            print(f"   ✗ Login failed: {str(e)}")
            driver.save_screenshot("error_login.png")
            return False
        
        # Check if we're logged in
        if "login" in driver.current_url.lower():
            print("   ⚠ Still on login page, login may have failed")
            driver.save_screenshot("login_failed_check.png")
            return False
        
        print("   ✓ Appears to be logged in successfully")
        return True
        
    except WebDriverException as e:
        print(f"❌ WebDriver Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            print("4. Closing browser...")
            driver.quit()
            print("   ✓ Browser closed")

if __name__ == "__main__":
    success = simple_booking()
    if success:
        print("\n✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Script failed!")
        sys.exit(1)
