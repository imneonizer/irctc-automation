import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
  

class Captcha:
    def __init__(self, driver, image, textbox, desc=""):
        self.driver = driver
        self.image = image
        self.textbox = textbox
        self.desc = desc
    
    def fill(self, text):
        if isinstance(self.textbox, str):
            captcha_box = self.driver.execute_script(f"return {self.textbox}")
        else:
            captcha_box = self.textbox
        
        captcha_box.clear()
        captcha_box.send_keys(text)
        captcha_box.send_keys(Keys.ENTER)
    
    def __repr__(self):
        return f"<{self.desc}>"

class Common:
    def __init__(self, driver):
        self.driver = driver
    
    def close_chatbox(self):
        try:
            self.driver.execute_script(f"""document.getElementById("corover-close-cb-btn").click();""")
        except: pass
    
    def sleep(self, s):
        self.driver.implicitly_wait(s)
    
    def scroll_to_element(self, e, sleep=0.03):
        self.driver.execute_script("arguments[0].scrollIntoView();", e)
        self.driver.execute_script("window.scrollBy(0, -100);")
        self.sleep(sleep)
        
    def click(self, e):
        self.scroll_to_element(e)
        self.driver.execute_script('arguments[0].click()', e)
        self.wait_until_loaded()
    
    @property
    def loading(self, sleep=0.03):
        try:
            self.driver.find_element_by_class_name("loading-bg")
            return True
        except NoSuchElementException:
            return False
    
    def wait_until_loaded(self, sleep=0.1):
        while self.loading:
            time.sleep(sleep)