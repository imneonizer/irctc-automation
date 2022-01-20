from PIL import Image
import io
import time
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import requests
from .common import Captcha, Common

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.login_page_url = "https://www.irctc.co.in/nget/train-search"
        self.error_page_url = "https://www.irctc.co.in/nget/error"
        self.common = Common(self.driver)
        self.captcha_text = ""
        
        # element selectors
        self.login_form_background = """document.getElementsByClassName("login-bg")[0]"""
        
        # self.login_form_open_button = """document.querySelector("#slide-menu > p-sidebar > div > nav > div > label > button")"""
        self.login_form_open_button = """document.querySelector("body > app-root > app-home > div:nth-child(1) > app-header > div.h_container_sm > div.h_menu_drop_button.moblogo.hidden-sm > a > label")"""
        self.side_bar = """document.getElementsByClassName("nav-bar")[1]"""
        
        self.login_form_close_button = """document.getElementsByClassName("loginCloseBtn")[0]"""
        self.username_box = """document.getElementsByTagName("input")[29]"""
        self.password_box = """document.getElementsByTagName("input")[30]"""
        
        # captcha selectors
        self.text_captcha = """document.querySelector("#captcha")"""
        self.text_captcha_image = """document.getElementsByClassName("captcha-img")[0]"""
        
        self.type_here_captcha = """document.querySelector("#nlpAnswer")"""
        self.type_here_captcha_image = """document.getElementById("nlpImgContainer")"""
        self.type_the_characters_captcha = """document.getElementById("nlpCaptchaImg")"""
        
        # clickable buttons
        self.signin_button = """document.getElementsByClassName("modal-body")[0]"""
        self.login_error_text = """document.getElementsByClassName("loginError")[0]"""
        self.logout_button = """document.getElementsByClassName("loginText")[1]"""
        
        # covid popup
        self.covid_popup = """document.getElementById("ui-dialog-1-label")"""
        self.covid_popup_close_button = """document.querySelector("body > app-root > app-home > div:nth-child(1) > app-header > p-dialog.ng-tns-c45-2 > div > div > div.ng-tns-c45-2.ui-dialog-content.ui-widget-content > div > form > div.text-center.col-xs-12 > button")"""
    
    def login_form_visible(self):
        return True if self.driver.execute_script(
            f"return {self.login_form_background};"
        ) else False
    
    def close_covid_popup(self):
        if self.driver.execute_script(f"return {self.covid_popup}"):
            self.driver.execute_script(f"{self.covid_popup_close_button}.click();")
    
    def sidebar_visible(self):
        return self.driver.execute_script("""return document.getElementsByClassName("nav-bar")[1]""").get_attribute("style") == "display: inherit;"
    
    def open_login_form(self, refresh=True, sleep=1):
        if self.driver.current_url != self.login_page_url:
            self.driver.get(self.login_page_url)
            self.common.sleep(sleep)
        
        if refresh and self.login_form_visible():
            # close login form to refresh captcha
            self.close_login_form()
        
        self.close_covid_popup()
        
        if not self.sidebar_visible():
            self.driver.execute_script(f"return {self.login_form_open_button}.click();")
        self.driver.execute_script("""return document.getElementsByClassName("search_btn")[3].click()""")
        
        time.sleep(sleep)
        self.common.wait_until_loaded()
        return True
    
    def close_login_form(self):
        return True if self.driver.execute_script(
            f"{self.login_form_close_button}.click(); return true"
        ) else False
    
    def logged_in(self):
        try:
            return True if self.driver.execute_script(f"return {self.logout_button}") else False
        except: pass
    
    def click_logout(self):
        if self.logged_in():
            self.driver.execute_script(f"{self.logout_button}.click()")
        self.driver.get(self.login_page_url)
        self.close_covid_popup()
    
    def fill_id_pass(self, username, password):
        self.common.close_chatbox()
        self.driver.execute_script(f"{self.username_box}.value = '';")
        self.common.close_chatbox()
        self.driver.execute_script(f"return {self.username_box};").send_keys(username)
        
        self.common.close_chatbox()
        self.driver.execute_script(f"{self.password_box}.value = '';")
        self.common.close_chatbox()
        self.driver.execute_script(f"return {self.password_box};").send_keys(password)
    
    def identify_captcha(self):
        # 1: text captcha
        # 2: type here captcha
        # 3: type the characters captcha
        
        self.common.close_chatbox()
        
        if self.driver.execute_script(f"return {self.text_captcha};"):
            captcha = self.driver.execute_script(f"return {self.text_captcha_image}")
            captcha = Image.open(io.BytesIO(captcha.screenshot_as_png)).convert("RGB")
            self.captcha = Captcha(self.driver, captcha, self.text_captcha, desc="text captcha")
            return self.captcha
        
        elif self.driver.execute_script(f"""return {self.type_here_captcha}.placeholder""") == "Type Here:":
            captcha = self.driver.execute_script(f"return {self.type_here_captcha_image}")
            captcha = captcha.find_elements_by_tag_name("img")[-1]
            # captcha = Image.open(io.BytesIO(captcha.screenshot_as_png)).convert("RGB")
            
            captcha = Image.open(io.BytesIO(requests.get(captcha.get_attribute("src")).content)).convert("RGB")
            width, height = captcha.size
            captcha = captcha.crop((155, 0, width, height)) # left, top, right, bottom

            self.captcha =  Captcha(self.driver, captcha, self.type_here_captcha, desc="type here captcha")
            return self.captcha
        
        # elif self.driver.execute_script(f"return {self.type_the_characters_captcha}"):
        #     captcha = self.driver.execute_script(f"return {self.type_the_characters_captcha}")
        #     captcha = Image.open(io.BytesIO(captcha.screenshot_as_png)).convert("RGB")
        #     # TODO: add captcha box selector
        #     self.captcha =  Captcha(self.driver, captcha, " ", desc="type the characters captcha")
        #     return self.captcha
    
    def get_captcha(self, refresh=True, max_retry=100, sleep=1):
        idx = 0
        while True:
            try:
                self.open_login_form(refresh=refresh, sleep=sleep)
                captcha = self.identify_captcha()
                if captcha: return captcha
            except:
                self.common.sleep(sleep)
                if max_retry and idx > max_retry: break
                idx += 1
    
    def fill_captcha(self, text):
        self.captcha_text = text
        self.common.close_chatbox()
        return self.captcha.fill(text)
        
    def click_signin(self, sleep=.5):
        self.common.close_chatbox()
        
        self.driver.execute_script(f"return {self.signin_button}").find_elements_by_tag_name("button")[0].click()
        self.common.sleep(sleep)
        self.common.wait_until_loaded()
        return self.signin_error()
    
    def signin_error(self):
        try:
            return self.driver.execute_script(f"return {self.login_error_text}.innerText")
        except: return ''
    
    def signin(self, username, password, captcha="", sleep=0.2):
        self.fill_id_pass(username, password)
        try:
            time.sleep(sleep)
            self.fill_captcha(captcha)
        except AttributeError: pass
        time.sleep(sleep)
        return self.click_signin()
    
    def handle_last_booking_incomplete_popup(self):
        try:
            if self.driver.find_element_by_class_name("ui-dialog-titlebar").text == "Last Transaction Detail":
                self.driver.find_element_by_class_name("ui-dialog-footer").find_element_by_tag_name("button").click()
        except NoSuchElementException: pass
    