import time
from selenium.common.exceptions import NoSuchElementException

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
    
    def __repr__(self):
        return f"<{self.desc}>"

class Common:
    def __init__(self, driver):
        self.driver = driver
    
    def close_chatbox(self):
        try:
            self.driver.execute_script(f"""document.getElementById("corover-close-cb-btn").click();""")
        except: pass
    
    def scroll_to_element(self, e, sleep=0.03):
        self.driver.execute_script("arguments[0].scrollIntoView();", e)
        self.driver.execute_script("window.scrollBy(0, -100);")
        time.sleep(sleep)
    
    @property
    def loading(self, sleep=1):
        try:
            time.sleep(sleep)
            self.driver.find_element_by_class_name("loading-bg")
            return True
        except NoSuchElementException:
            return False
    
    def wait_until_loaded(self, sleep=0.03):
        while self.loading:
            time.sleep(sleep)