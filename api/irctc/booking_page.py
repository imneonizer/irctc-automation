from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from .common import Common
import time

class BookingPage:
    def __init__(self, driver):
        self.driver = driver
        self.common = Common(self.driver)
    
    @property
    def booking_tab_visible(self):
        # confirm if boooking page is open
        if self.driver.execute_script("""return document.getElementsByClassName("jp-radious")"""):
            return True
        return False
    
    @property
    def loading(self, sleep=1):
        try:
            time.sleep(sleep)
            self.driver.find_element_by_class_name("loading-bg")
            return True
        except NoSuchElementException:
            return False
    
    def click_body(self):
        self.common.close_chatbox()
        self.driver.find_element_by_tag_name("body").click()
    
    def fill_origin(self, station_code, sleep=0.3):
        self.common.close_chatbox()
        origin = self.driver.execute_script("""return document.getElementById("origin")""")
        origin = origin.find_element_by_tag_name("input")
        origin.clear()
        origin.send_keys(station_code.upper())
        time.sleep(sleep)
        origin.send_keys(Keys.ENTER)
    
    def fill_destination(self, station_code, sleep=0.3):
        self.common.close_chatbox()
        destination = self.driver.execute_script("""return document.getElementById("destination")""")
        destination = destination.find_element_by_tag_name("input")
        destination.clear()
        destination.send_keys(station_code.upper())
        time.sleep(sleep)
        
        destination.send_keys(Keys.ENTER)
    
    def fill_date(self, date_string, sleep=0.3):
        # format: dd/mm/yyyy
        self.common.close_chatbox()
        journey_date = self.driver.find_element_by_tag_name("p-calendar").find_element_by_tag_name("input")
        self.click_body()
        journey_date.send_keys(Keys.CONTROL, 'a')
        journey_date.send_keys(Keys.BACKSPACE)
        journey_date.send_keys(date_string)
        journey_date.send_keys(Keys.ESCAPE)
        self.click_body()

    def fill_class(self, journey_class, sleep=0.03):
        # Note: only pass class code e.g., SL
        
        # Anubhuti Class (EA)
        # AC First Class (1A)
        # Exec. Chair Car (EC)
        # AC 2 Tier (2A)
        # First Class (FC)
        # AC 3 Tier (3A)
        # AC 3 Economy (3E)
        # AC Chair car (CC)
        # Sleeper (SL)
        # Second Sitting (2S)
        
        self.common.close_chatbox()
        
        # Make sure dropdown menu is visible
        if "ui-dropdown-open" not in self.driver.find_element_by_id("journeyClass").find_element_by_tag_name("div").get_attribute("class"):
            self.common.close_chatbox()
            self.driver.find_element_by_id("journeyClass").click()
            time.sleep(sleep)
        
        # iterate through dropdown items to select journey class
        dropdown_items = self.driver.find_elements_by_tag_name("p-dropdownitem")
        for i, e in enumerate(dropdown_items):
            if f"({journey_class})" in e.text:
                self.common.close_chatbox()
                e.click()
    
    def fill_quota(self, journey_quota, sleep=0.03):
        # GENERAL
        # LADIES
        # LOWER BERTH/SR.CITIZEN
        # DIVYAANG
        # TATKAL
        # PREMIUM TATKAL
        
        self.common.close_chatbox()
        
        # Make sure dropdown menu is visible
        if "ui-dropdown-open" not in self.driver.find_element_by_id("journeyQuota").find_element_by_tag_name("div").get_attribute("class"):
            self.common.close_chatbox()
            self.driver.find_element_by_id("journeyQuota").click()
            time.sleep(sleep)

        # iterate through dropdown items to select journey quota
        dropdown_items = self.driver.find_elements_by_tag_name("p-dropdownitem")
        for i, e in enumerate(dropdown_items):
            if journey_quota.upper() in e.text:
                self.common.close_chatbox()
                e.click()
    
    def select_checkboxes(self, options={}, sleep=0.1):        
        default_options = {
            "divyaang_concession": False,
            "flexible_with_date": False,
            "train_with_available_berth": False,
            "railway_pass_concession": False
        }
        
        default_options.update(options)

        for e in self.driver.find_elements_by_class_name("css-label_c"):
            opt = e.text.replace(" ", "_").lower()
            checkbox = self.driver.find_element_by_id(e.get_attribute("for"))
            
            if default_options.get(opt) == True:
                # if we want to select this option
                if not checkbox.is_selected():
                    # select if not already selected
                    self.common.close_chatbox()
                    e.click()
            else:
                # if we dont't want to select this option
                if checkbox.is_selected():
                    # dis-select if already selected
                    self.common.close_chatbox()
                    e.click()
            
            # if we selected any option
            if default_options.get(opt) == True:
                # then wait for confirmation box to appear
                time.sleep(sleep)
            
            try:
                # bypass the confirmation box, if appear
                if self.driver.find_element_by_class_name("ui-dialog-title"):
                    self.common.close_chatbox()
                    self.driver.find_element_by_class_name("ui-button-text").click()
            except NoSuchElementException: pass
    
    @property
    def error_toast(self):
        try:
            error = self.driver.find_element_by_tag_name("p-toastitem").find_element_by_class_name("ui-toast-detail").text
            return error
        except NoSuchElementException:
            return ''
    
    def click_search(self):
        # press search train button
        self.common.close_chatbox()
        self.driver.find_element_by_tag_name("button").click()
    
    @property
    def train_list_page_visible(self):
        return True if self.driver.execute_script("""return document.getElementsByClassName("fa-long-arrow-left")""") else False
    
    def go_back(self):
        if self.train_list_page_visible:
            self.common.close_chatbox()
            self.driver.find_element_by_class_name("fa-long-arrow-left").click()
    
    def wait_until_loaded(self, sleep=0.03):
        while self.loading:
            time.sleep(sleep)