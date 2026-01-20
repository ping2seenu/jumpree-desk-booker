import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

class JumpreeDeskBooking:
    def __init__(self, email, password, headless=False):
        """
        Initialize the Jumpree booking automation
        
        Args:
            email (str): srinivasareddy.kumbagiri@juliusbaer.com
            password (str): Forgot@123
            headless (bool): Run browser in headless mode
        """
        self.email = email
        self.password = password
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.logger.info("Chrome driver initialized")

    def login(self):
        """Login to Jumpree platform"""
        try:
            # Open login page
            self.driver.get("https://jumpree.smartenspaces.com/")
            self.logger.info("Opened Jumpree login page")
            time.sleep(3)
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            self.logger.info("Email entered")
            
            # Click proceed button
            proceed_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "submit_btn"))
            )
            proceed_btn.click()
            self.logger.info("Clicked proceed button")
            time.sleep(2)
            
            # Enter password
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("Password entered")
            
            # Check terms and conditions if needed
            try:
                terms_checkbox = self.driver.find_element(By.CSS_SELECTOR, "#acceptTerms-input")
                if not terms_checkbox.is_selected():
                    terms_checkbox.click()
                    self.logger.info("Accepted terms and conditions")
            except:
                self.logger.warning("Could not find terms checkbox, continuing...")
            
            # Click login button - try different selectors
            login_selectors = [
                "//button[@id='submit_btn' and contains(text(), 'Login')]",
                "//button[contains(@class, 'loginBtnButtomNew')]",
                "//button[contains(text(), 'Login')]"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    login_btn.click()
                    self.logger.info("Clicked login button")
                    break
                except:
                    continue
            
            # Wait for login to complete
            time.sleep(5)
            
            # Verify login success
            if any(keyword in self.driver.current_url.lower() for keyword in ["dashboard", "layout", "home"]):
                self.logger.info("Login successful")
                return True
            else:
                # Take screenshot for debugging
                self.driver.save_screenshot("login_issue.png")
                self.logger.error("Login may have failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            return False

    def navigate_to_booking(self):
        """Navigate to booking section"""
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Click on Booking menu - try different selectors
            booking_selectors = [
                (By.ID, "amenity_booking"),
                (By.XPATH, "//a[contains(@href, 'amenity-booking')]"),
                (By.XPATH, "//span[contains(text(), 'Booking')]/.."),
                (By.XPATH, "//*[contains(text(), 'Booking')]")
            ]
            
            for selector in booking_selectors:
                try:
                    booking_menu = self.wait.until(
                        EC.element_to_be_clickable(selector)
                    )
                    booking_menu.click()
                    self.logger.info("Navigated to booking section")
                    time.sleep(3)
                    break
                except:
                    continue
            
            # Look for Book Now button
            book_now_selectors = [
                (By.ID, "book_now_amenity"),
                (By.XPATH, "//button[contains(text(), 'Book Now')]"),
                (By.XPATH, "//button[contains(@class, 'btn-main') and contains(text(), 'Book')]")
            ]
            
            for selector in book_now_selectors:
                try:
                    book_now_btn = self.wait.until(
                        EC.element_to_be_clickable(selector)
                    )
                    book_now_btn.click()
                    self.logger.info("Clicked Book Now button")
                    time.sleep(3)
                    break
                except:
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation to booking failed: {str(e)}")
            self.driver.save_screenshot("navigation_error.png")
            return False

    def select_date(self, target_date=None):
        """
        Select booking date
        
        Args:
            target_date (datetime.date): Date to book (default: tomorrow)
        """
        try:
            if target_date is None:
                # Default to tomorrow
                target_date = datetime.date.today() + datetime.timedelta(days=1)
            
            self.logger.info(f"Selecting date: {target_date}")
            
            # Find calendar icon
            calendar_selectors = [
                (By.XPATH, "//img[contains(@src, 'calendar')]"),
                (By.CLASS_NAME, "fa-calendar"),
                (By.XPATH, "//*[contains(text(), 'Select Date')]")
            ]
            
            for selector in calendar_selectors:
                try:
                    calendar_element = self.wait.until(
                        EC.element_to_be_clickable(selector)
                    )
                    calendar_element.click()
                    self.logger.info("Opened calendar")
                    time.sleep(2)
                    break
                except:
                    continue
            
            # Try to select the date
            # This is the tricky part - you'll need to inspect your calendar
            day_to_select = target_date.day
            
            # Try multiple strategies for date selection
            date_found = False
            
            # Strategy 1: Click on day number
            try:
                date_element = self.driver.find_element(
                    By.XPATH, f"//td[contains(@class, 'day') and text()='{day_to_select}']"
                )
                date_element.click()
                date_found = True
                self.logger.info(f"Selected day {day_to_select} using Strategy 1")
            except:
                pass
            
            # Strategy 2: Try with aria-label or data attributes
            if not date_found:
                try:
                    date_str = target_date.strftime("%Y-%m-%d")
                    date_element = self.driver.find_element(
                        By.XPATH, f"//*[@data-date='{date_str}']"
                    )
                    date_element.click()
                    date_found = True
                    self.logger.info(f"Selected date {date_str} using Strategy 2")
                except:
                    pass
            
            # Strategy 3: Try with button containing date
            if not date_found:
                try:
                    date_element = self.driver.find_element(
                        By.XPATH, f"//button[contains(text(), '{day_to_select}')]"
                    )
                    date_element.click()
                    date_found = True
                    self.logger.info(f"Selected day {day_to_select} using Strategy 3")
                except:
                    pass
            
            if not date_found:
                self.logger.warning("Could not select date automatically. Please select manually.")
                time.sleep(10)  # Give time for manual selection
                self.driver.save_screenshot("date_selection.png")
            
            time.sleep(2)
            
            # Click Next button
            next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
            for btn in next_buttons:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    self.logger.info("Clicked Next button")
                    break
            
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Date selection failed: {str(e)}")
            self.driver.save_screenshot("date_error.png")
            return False

    def select_location_and_desk(self, building="ONE@CHANGI CITY", level="06"):
        """
        Select building, level, and specific desk
        
        Args:
            building (str): Building name
            level (str): Floor level
        """
        try:
            # Wait for location selection page
            time.sleep(3)
            
            # Find building
            building_found = False
            building_selectors = [
                f"//*[contains(text(), '{building}')]",
                f"//p[contains(text(), '{building}')]"
            ]
            
            for selector in building_selectors:
                try:
                    building_element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    self.logger.info(f"Found building: {building}")
                    building_found = True
                    break
                except:
                    continue
            
            if not building_found:
                self.logger.warning(f"Building '{building}' not found")
            
            # Select level
            level_found = False
            level_selectors = [
                f"//*[contains(text(), 'Level {level}')]",
                f"//p[contains(text(), 'Level {level}')]"
            ]
            
            for selector in level_selectors:
                try:
                    level_element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    level_element.click()
                    self.logger.info(f"Selected level: {level}")
                    level_found = True
                    break
                except:
                    continue
            
            if not level_found:
                self.logger.warning(f"Level {level} not found. Trying dropdown...")
                # Try clicking dropdown first
                try:
                    dropdown = self.driver.find_element(By.XPATH, "//i[contains(@class, 'fa-angle-down')]")
                    dropdown.click()
                    time.sleep(1)
                    
                    # Now try selecting level
                    level_element = self.driver.find_element(By.XPATH, f"//*[contains(text(), 'Level {level}')]")
                    level_element.click()
                    self.logger.info(f"Selected level {level} from dropdown")
                except:
                    self.logger.error("Could not select level")
            
            time.sleep(3)
            
            # Try to select a desk (if interactive map)
            try:
                # Look for desk markers or selectable elements
                desk_selectors = [
                    "//img[contains(@src, 'entitySelectedDwg.svg')]",
                    "//div[contains(@class, 'desk')]",
                    "//*[contains(@class, 'leaflet-interactive')]",
                    "//button[contains(text(), 'Select')]"
                ]
                
                for selector in desk_selectors:
                    try:
                        desks = self.driver.find_elements(By.XPATH, selector)
                        if desks:
                            # Click the first available desk
                            desks[0].click()
                            self.logger.info("Selected a desk")
                            time.sleep(2)
                            break
                    except:
                        continue
            except:
                self.logger.warning("Could not select desk automatically")
            
            # Click Next to proceed
            next_found = False
            for _ in range(3):  # Try multiple times
                next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
                for btn in next_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        self.logger.info("Clicked Next to proceed")
                        next_found = True
                        time.sleep(3)
                        break
                if next_found:
                    break
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Location/desk selection failed: {str(e)}")
            self.driver.save_screenshot("location_error.png")
            return False

    def confirm_booking(self):
        """Final booking confirmation"""
        try:
            # Wait for booking confirmation page
            time.sleep(3)
            
            # Look for final Book Now button
            book_now_selectors = [
                (By.ID, "save_booking"),
                (By.XPATH, "//button[contains(text(), 'Book Now')]"),
                (By.XPATH, "//button[contains(text(), 'Confirm')]"),
                (By.XPATH, "//button[contains(@class, 'btn-primary')]")
            ]
            
            for selector in book_now_selectors:
                try:
                    book_now_final = self.wait.until(
                        EC.element_to_be_clickable(selector)
                    )
                    book_now_final.click()
                    self.logger.info("Clicked final Book Now button")
                    time.sleep(5)
                    break
                except:
                    continue
            
            # Check for success
            time.sleep(3)
            page_text = self.driver.page_source.lower()
            success_keywords = ["success", "confirmed", "booked", "thank you", "reserved"]
            
            if any(keyword in page_text for keyword in success_keywords):
                self.logger.info("✅ Booking appears to be successful!")
                self.driver.save_screenshot("booking_success.png")
                return True
            else:
                self.logger.warning("⚠️ Booking completion uncertain. Please check manually.")
                self.driver.save_screenshot("booking_uncertain.png")
                return False
                
        except Exception as e:
            self.logger.error(f"Booking confirmation failed: {str(e)}")
            self.driver.save_screenshot("confirmation_error.png")
            return False

    def book_desk(self, target_date=None, building="ONE@CHANGI CITY", level="06"):
        """
        Complete desk booking flow
        
        Args:
            target_date (datetime.date): Date to book
            building (str): Building name
            level (str): Floor level
        """
        try:
            self.logger.info("🚀 Starting desk booking process")
            
            # Step 1: Login
            self.logger.info("Step 1: Logging in...")
            if not self.login():
                self.logger.error("Login failed. Stopping.")
                return False
            
            # Step 2: Navigate to booking
            self.logger.info("Step 2: Navigating to booking...")
            if not self.navigate_to_booking():
                self.logger.error("Navigation failed. Stopping.")
                return False
            
            # Step 3: Select date
            self.logger.info("Step 3: Selecting date...")
            if not self.select_date(target_date):
                self.logger.warning("Date selection may have issues. Continuing...")
                # Continue anyway to see if we can proceed
            
            # Step 4: Select location and desk
            self.logger.info("Step 4: Selecting location and desk...")
            if not self.select_location_and_desk(building, level):
                self.logger.warning("Location/desk selection may have issues. Continuing...")
            
            # Step 5: Confirm booking
            self.logger.info("Step 5: Confirming booking...")
            if not self.confirm_booking():
                self.logger.warning("Booking confirmation may have issues.")
                return False
            
            self.logger.info("🎉 Desk booking process completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Booking process failed: {str(e)}")
            return False

    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
            self.logger.info("Browser closed")
        except:
            pass

    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot for debugging"""
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved as {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")


# Main execution - simple and manual
if __name__ == "__main__":
    print("=" * 50)
    print("JUMPREE DESK BOOKING AUTOMATION")
    print("=" * 50)
    
    # Get credentials from user input
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    
    # Optional: Get booking preferences
    print("\nBooking Preferences (press Enter for defaults):")
    building = input(f"Building [default: ONE@CHANGI CITY]: ").strip() or "ONE@CHANGI CITY"
    level = input(f"Level [default: 06]: ").strip() or "06"
    
    # Ask for date
    print("\nBooking Date:")
    print("1. Tomorrow (default)")
    print("2. Custom date")
    choice = input("Select option [1-2]: ").strip()
    
    if choice == "2":
        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            print("Invalid date format. Using tomorrow instead.")
            target_date = datetime.date.today() + datetime.timedelta(days=1)
    else:
        target_date = datetime.date.today() + datetime.timedelta(days=1)
    
    print("\n" + "=" * 50)
    print(f"Booking Summary:")
    print(f"  Email: {email}")
    print(f"  Date: {target_date}")
    print(f"  Building: {building}")
    print(f"  Level: {level}")
    print("=" * 50)
    
    confirm = input("\nStart booking? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Booking cancelled.")
        exit()
    
    print("\nStarting automation...")
    
    # Initialize and run booking (not headless so you can see what's happening)
    booking_bot = JumpreeDeskBooking(email, password, headless=False)
    
    try:
        success = booking_bot.book_desk(
            target_date=target_date,
            building=building,
            level=level
        )
        
        if success:
            print("\n" + "=" * 50)
            print("✅ BOOKING COMPLETED SUCCESSFULLY!")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("⚠️ BOOKING MAY HAVE FAILED OR NEEDS MANUAL CHECK")
            print("=" * 50)
            print("Check the screenshots and logs for details.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        booking_bot.take_screenshot("critical_error.png")
    finally:
        # Ask before closing
        keep_open = input("\nKeep browser open for inspection? (y/n): ").strip().lower()
        if keep_open != 'y':
            booking_bot.close()
            print("Browser closed.")
        else:
            print("Browser will remain open. Close it manually when done.")
