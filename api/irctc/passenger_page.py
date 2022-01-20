from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from .common import Common
from PIL import Image
import requests
import io
import time
from .common import Captcha

class PassengerPage:
    def __init__(self, driver, booking_page):
        self.driver = driver
        self.common = Common(driver)
    
    def remove_all_passengers(self):
        for e in self.driver.find_elements_by_class_name("fa-remove"):
            self.common.close_chatbox()
            self.common.click(e)
    
    def scroll_to_add_passenger(self):
        add_passenger = self.driver.find_element_by_link_text("+ Add Passenger")
        self.driver.execute_script("arguments[0].scrollIntoView();", add_passenger)
        self.driver.execute_script("window.scrollBy(0, -300);")
    
    def create_n_passengers(self, n):
        self.remove_all_passengers()
        for i in range(n):
            self.scroll_to_add_passenger()
            self.common.close_chatbox()
            add_passenger = self.driver.find_element_by_class_name("prenext")
            self.common.click(add_passenger)
    
    def num_passengers(self):
        return len(self.driver.find_elements_by_class_name("fa-remove"))
    
    def fill_passengers(self, details):
        # details: list of dict
        self.common.close_chatbox()
        self.create_n_passengers(len(details))
        
        # fill input boxes
        for i, form in enumerate(self.driver.find_elements_by_tag_name("app-passenger")):
            for e in form.find_elements_by_tag_name("input"):
                placeholder = e.get_attribute("placeholder")
                
                self.common.close_chatbox()
                    
                if placeholder  == "Passenger Name":
                    e.clear()
                    e.send_keys(details[i].get("name")[:16].title())
                    
                elif placeholder == "Age":
                    e.clear()
                    e.send_keys(details[i].get("age"))
        
        # select dropdown items
        for i, form in enumerate(self.driver.find_elements_by_tag_name("app-passenger")):
            for e in form.find_elements_by_tag_name("select"):
                self.common.close_chatbox()
                
                placeholder = e.get_attribute("formcontrolname")
                e = Select(e)
                
                if placeholder == "passengerGender":
                    e.select_by_visible_text(details[i].get("gender").title())
                    
                elif placeholder == "passengerNationality":
                    e.select_by_visible_text(details[i].get("nationality").title())
                    
                elif placeholder == "passengerBerthChoice":
                    e.select_by_visible_text(details[i].get("preference").title())
    
    def fill_address(self, address, sleep=0.3):
        for e in self.driver.find_element_by_tag_name("app-address-capture").find_elements_by_tag_name("input"):
            self.common.close_chatbox()
            
            if e.get_attribute("placeholder") == "Correspondence 1 *":    
                e.clear()
                e.send_keys(address.get("city").title())

            elif e.get_attribute("placeholder") == "PIN *":
                e.clear()
                e.send_keys(address.get("pincode"))
                e.send_keys(Keys.ENTER)

            elif e.get_attribute("placeholder") == "State *":
                self.common.click(e)

        self.common.sleep(sleep)
        
        try:
            self.common.close_chatbox()
            e = Select(self.driver.find_element_by_id("address-City"))
            e.select_by_index(1)
        except: pass
        
        try:
            self.common.close_chatbox()
            e = Select(self.driver.find_element_by_id("address-postOffice"))
            e.select_by_index(1)
        except: pass
    
    def fill_number(self, number):
        self.common.close_chatbox()
        mobile_number_input = self.driver.find_element_by_id("mobileNumber")
        self.common.scroll_to_element(mobile_number_input)
        mobile_number_input.clear()
        mobile_number_input.send_keys(number)
    
    def fill_details(self, details, sleep=0.1):
        self.fill_passengers(details["passengers"])
        
        self.common.sleep(sleep)
        self.fill_number(details["mobile"])
        
        self.common.sleep(sleep)
        self.fill_address({"city": details["city"], "pincode": details["pincode"]})
        
        self.common.sleep(sleep)
        self.select_insurance(details["travel_insurance"])
        
        self.common.sleep(sleep)
        self.select_payment_mode(details["payment_mode"])
        
        self.common.sleep(sleep)
        self.click_submit()
    
    def click_submit(self):
        self.common.close_chatbox()
        submit_button = self.driver.find_elements_by_class_name("mob-bot-btn")[1]
        self.common.scroll_to_element(submit_button)
        self.common.click(submit_button)
        self.common.wait_until_loaded()
    
    def identify_captcha(self):
        if self.driver.find_element_by_id("nlpAnswer"):
            captcha = self.driver.find_element_by_id("nlpImgContainer").find_elements_by_tag_name("img")[1].get_attribute("src")
            captcha = Image.open(io.BytesIO(requests.get(captcha).content)).convert("RGB")
            self.captcha = Captcha(self.driver, captcha, self.driver.find_element_by_id("nlpAnswer"), desc="type here captcha")
            return self.captcha
    
    def get_captcha(self, max_retry=100, sleep=1):
        idx = 0
        while True:
            try:
                captcha = self.identify_captcha()
                if captcha: return captcha
            except:
                self.common.sleep(sleep)
                if max_retry and idx > max_retry: break
                idx += 1
    
    def fill_captcha(self, text):
        self.captcha.fill(text)

    def select_insurance(self, travel_insurance=True):
        e = self.driver.find_element_by_id("travelInsuranceOptedYes-0")
        self.driver.execute_script("arguments[0].scrollIntoView();", e)
        self.driver.execute_script("window.scrollBy(0, -300);")
        if travel_insurance:
            self.common.close_chatbox()
            self.common.click(self.driver.find_element_by_id("travelInsuranceOptedYes-0"))
        else:
            self.common.close_chatbox()
            self.common.click(self.driver.find_element_by_id("travelInsuranceOptedNo-0"))
            
    
    def select_payment_mode(self, mode):
        payment_modes = {"net_banking": 0, "upi": 1}
        for i, e in enumerate(self.driver.find_elements_by_tag_name("p-radiobutton")[2:]):
            if payment_modes[mode] == i:
                self.driver.execute_script("arguments[0].scrollIntoView();", e)
                self.driver.execute_script("window.scrollBy(0, -300);")
                self.common.close_chatbox()
                self.common.click(e)
    
    def is_journey_page(self):
        try:
            return self.driver.find_element_by_tag_name("app-journey-details")
        except: pass
    
    def select_paytm_payment(self, sleep=0.1):
        # select multiple payment service
        for e in self.driver.find_elements_by_class_name("bank-type"):
            if "Multiple Payment Service" in e.text:
                self.common.click(e)
        
        self.common.sleep(sleep)
        
        # click on continue
        for e in self.driver.find_elements_by_class_name("mob-bot-btn"):
            if e.text == "Continue":
                self.common.click(e)
        
        self.common.sleep(sleep)
        
        # select paytm
        for e in self.driver.find_elements_by_class_name("bank-text"):
            if "Paytm" in e.text:
                self.common.click(e) 
        
        self.common.sleep(sleep)
        
        # click pay & book
        for e in self.driver.find_elements_by_class_name("mob-bot-btn"):
            if e.text == "Pay & Book":
                self.common.click(e)