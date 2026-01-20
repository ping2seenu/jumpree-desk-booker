import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIGURATION =================
# REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
EMAIL = "srinivasareddy.kumbagiri@juliusbaer.com"  # <-- CHANGE THIS
PASSWORD = "Forgot@123"  # <-- CHANGE THIS
BUILDING = "ONE@CHANGI CITY"
LEVEL = "06"
DAYS_AHEAD = 1  # Book for tomorrow
# ================================================

def main():
    print("Starting Jumpree Desk Booking...")
    print(f"Email: {EMAIL}")
    
    if EMAIL == "your_email@domain.com" or PASSWORD == "your_password_here":
        print("\n❌ ERROR: Please edit the script and replace the email and password!")
        print("Open the file and change these lines:")
        print("  EMAIL = 'your.email@domain.com'  ->  EMAIL = 'your_real_email@company.com'")
        print("  PASSWORD = 'your_password_here'   ->  PASSWORD = 'your_real_password'")
        return
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        print("1. Setting up Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        # Step 1: Login
        print("2. Logging in...")
        driver.get("https://jumpree.smartenspaces.com/")
        time.sleep(3)
        
        # Enter email
        driver.find_element(By.ID, "email").send_keys(EMAIL)
        driver.find_element(By.ID, "submit_btn").click()
        time.sleep(2)
        
        # Enter password
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        
        # Accept terms if exists
        try:
            terms = driver.find_element(By.CSS_SELECTOR, "#acceptTerms-input")
            if not terms.is_selected():
                terms.click()
        except:
            pass
        
        # Click login
        login_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login')]")
        for btn in login_btns:
            if btn.is_displayed():
                btn.click()
                break
        
        time.sleep(5)
        print("✓ Logged in")
        
        # Step 2: Go to booking
        print("3. Going to booking section...")
        booking_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'amenity-booking')]")))
        booking_link.click()
        time.sleep(3)
        
        # Step 3: Click Book Now
        print("4. Starting new booking...")
        book_now_btn = wait.until(EC.element_to_be_clickable((By.ID, "book_now_amenity")))
        book_now_btn.click()
        time.sleep(3)
        
        # Step 4: Select date
        print("5. Selecting date...")
        calendar_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'calendar')]")))
        calendar_icon.click()
        time.sleep(2)
        
        # Select tomorrow (or specified days ahead)
        target_date = datetime.date.today() + datetime.timedelta(days=DAYS_AHEAD)
        day_to_select = target_date.day
        
        # Try to click the date
        try:
            # Look for the day number
            date_elements = driver.find_elements(By.XPATH, f"//td[text()='{day_to_select}']")
            for elem in date_elements:
                if elem.is_displayed():
                    elem.click()
                    print(f"✓ Selected date: {target_date}")
                    break
        except:
            print(f"⚠ Could not auto-select date {day_to_select}. Please select manually.")
            time.sleep(10)
        
        time.sleep(2)
        
        # Click Next
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")))
        next_btn.click()
        time.sleep(3)
        
        # Step 5: Select location and desk
        print("6. Selecting location and desk...")
        
        # Wait for building to load
        time.sleep(3)
        
        # Select level
        try:
            dropdown = driver.find_element(By.XPATH, "//i[contains(@class, 'fa-angle-down')]")
            dropdown.click()
            time.sleep(1)
            
            # Click level option
            level_options = driver.find_elements(By.XPATH, f"//*[contains(text(), 'Level {LEVEL}')]")
            for option in level_options:
                if option.is_displayed():
                    option.click()
                    print(f"✓ Selected level {LEVEL}")
                    break
        except:
            print("⚠ Could not select level automatically")
        
        time.sleep(3)
        
        # Try to select a desk
        try:
            # Look for desk markers
            markers = driver.find_elements(By.XPATH, "//img[contains(@src, 'entitySelectedDwg.svg')]")
            if markers:
                markers[0].click()
                print("✓ Selected a desk")
                time.sleep(2)
        except:
            print("⚠ Could not auto-select desk")
        
        # Click Next
        next_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
        for btn in next_btns:
            if btn.is_displayed():
                btn.click()
                break
        
        time.sleep(3)
        
        # Step 6: Final confirmation
        print("7. Confirming booking...")
        final_book_btn = wait.until(EC.element_to_be_clickable((By.ID, "save_booking")))
        final_book_btn.click()
        time.sleep(5)
        
        print("=" * 50)
        print("✅ BOOKING PROCESS COMPLETED!")
        print("=" * 50)
        print("\nPlease check if booking was successful.")
        print("Browser will stay open for 60 seconds...")
        
        time.sleep(60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        # Take screenshot
        try:
            driver.save_screenshot("error.png")
            print("Screenshot saved as error.png")
        except:
            pass
    finally:
        try:
            driver.quit()
            print("Browser closed")
        except:
            pass

if __name__ == "__main__":
    main()
