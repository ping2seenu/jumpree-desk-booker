import json
import schedule
import time
from datetime import datetime, timedelta

class BookingScheduler:
    def __init__(self, config_file="booking_config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load booking configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "email": "srinivasareddy.kumbagiri@juliusbaer.com",
                "password": "Forgot@123",
                "default_building": "ONE@CHANGI CITY",
                "default_level": "06",
                "booking_time": "08:00",  # Time to run booking daily
                "advance_days": 1,  # Book 1 day in advance
                "enabled": True
            }
            self.save_config()
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def schedule_daily_booking(self):
        """Schedule daily booking at specified time"""
        schedule.every().day.at(self.config["booking_time"]).do(self.run_booking)
        
        print(f"📅 Booking scheduled daily at {self.config['booking_time']}")
        print("Press Ctrl+C to stop")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_booking(self):
        """Execute booking"""
        from jumpree_booking import JumpreeDeskBooking
        
        print(f"🚀 Starting scheduled booking at {datetime.now()}")
        
        target_date = datetime.now() + timedelta(days=self.config["advance_days"])
        
        bot = JumpreeDeskBooking(
            email=self.config["email"],
            password=self.config["password"],
            headless=True
        )
        
        try:
            success = bot.book_desk(
                target_date=target_date.date(),
                building=self.config["default_building"],
                level=self.config["default_level"]
            )
            
            if success:
                print(f"✅ Successfully booked for {target_date.date()}")
            else:
                print("❌ Booking failed")
                bot.take_screenshot(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            bot.close()

# Configuration file template (booking_config.json)
CONFIG_TEMPLATE = {
    "email": "your_email@domain.com",
    "password": "your_password",
    "default_building": "ONE@CHANGI CITY",
    "default_level": "06",
    "booking_time": "08:00",
    "advance_days": 1,
    "enabled": true
}
