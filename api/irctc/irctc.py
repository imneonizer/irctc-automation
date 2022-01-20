# import imchrome
from selenium import webdriver
from .login_page import LoginPage
from .booking_page import BookingPage
from .search_page import SearchPage
from .passenger_page import PassengerPage
from .common import Common
from .captcha_solver import ocr
import time
import datetime

class Irctc:
    def __init__(self, chrome=None, chromedriver="chromedriver/linux64/chromedriver", headless=False, window_size=(700, 1000)):
        self.headless = headless
        self.chromedriver = chromedriver
        self.window_size = window_size
        self.chrome = chrome or self.init_chrome()
        self.driver = self.chrome.driver
        self.ocr = ocr
        
        if not self.chrome_reachable:
            self.chrome = self.init_chrome()
        
        self.chrome.driver.set_window_size(*self.window_size)
        self.login_page = LoginPage(self.chrome.driver)
        self.booking_page = BookingPage(self.chrome.driver)
        self.search_page = SearchPage(self.chrome.driver, self.login_page, self.booking_page)
        self.passenger_page = PassengerPage(self.chrome.driver, self.booking_page)
        self.common = Common(self.chrome.driver)
        
        self.username = None
        self.password = None
        self.login_at = None
        self.login_elapsed = None
        self.irctc_clock = None
    
    def init_chrome(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver',options=options)
        
        class Chrome:
            def __init__(self, driver):
                self.driver = driver
        
        self.chrome = Chrome(self.driver)
        
        # self.chrome = imchrome.init(chromedriver=self.chromedriver, headless=self.headless, load_image=True)
        # self.driver = self.chrome.driver
        self.chrome.driver.set_window_size(*self.window_size)
        return self.chrome
    
    @property
    def chrome_reachable(self):
        try:
            self.chrome.driver.window_handles
            return True
        except: return False
    
    # def clock(self):
    #     if not self.irctc_clock:
    #         self.irctc_clock = self.chrome.driver.find_element_by_tag_name("p-sidebar").find_element_by_tag_name("strong")
    #     return datetime.datetime.strptime(self.irctc_clock.text, "%d-%b-%Y [%H:%M:%S]")
    
    def login(self, username, password, max_retry=100, sleep=1, print_captcha=False):
        if self.login_page.logged_in():
            return True
        
        st = time.time()
        
        if not self.chrome_reachable:
            self.init_chrome()
                
        idx = 0
        while True:
            if self.login_page.logged_in():
                self.username = username
                self.password = password
                self.login_at = time.time()
                self.login_elapsed = time.time() - st
                print(f"Logged in as {self.username} on {datetime.datetime.fromtimestamp(self.login_at)}")
                print(f"Elapsed: {round(self.login_elapsed, 3)} sec")
                return True
            
            self.login_page.get_captcha(refresh=True, sleep=sleep)
            captcha = ocr.predict(self.login_page.captcha.image)
            if print_captcha: print(f"Captcha: {captcha}")
            
            try:
                self.login_page.signin(username, password, captcha)
                self.login_page.handle_last_booking_incomplete_popup()
            except: pass
            
            if max_retry and idx >= max_retry: break
            idx +=1
            time.sleep(sleep)
        
        print(f"Unable to solve captcha after ({max_retry}) retries")
        # TODO: add logic to send captcha over telegram for the user to enter

    def fill_passenger_details(self, details, max_retry=100, sleep=1, print_captcha=True):
        time.sleep(sleep)
        self.passenger_page.fill_details(details)
        
        idx = 0
        while True:
            if self.passenger_page.is_journey_page():
                return True
            
            captcha = self.passenger_page.get_captcha()
            captcha_text = self.ocr.predict(captcha.image)
            captcha.fill(captcha_text)
            if print_captcha: print(f"Captcha: {captcha_text}")
            
            self.passenger_page.click_submit()
            
            if max_retry and idx >= max_retry: break
            idx +=1
            time.sleep(sleep)
        
        print(f"Unable to solve captcha after ({max_retry}) retries")
        # TODO: add logic to send captcha over telegram for the user to enter
        
    def search_train(self, details):
        time.sleep(1)
        return self.search_page.search_train(details)
    
    def logout(self):
        if self.login_page.logged_in():
            self.login_page.click_logout()
        return (not self.login_page.logged_in())