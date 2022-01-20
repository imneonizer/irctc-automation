from selenium.webdriver.support.select import Select
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
            self.common.scroll_to_element(e)
            e.click()
    
    def scroll_to_add_passenger(self):
        add_passenger = self.driver.find_element_by_link_text("+ Add Passenger")
        self.driver.execute_script("arguments[0].scrollIntoView();", add_passenger)
        self.driver.execute_script("window.scrollBy(0, -300);")
    
    def create_n_passengers(self, n):
        self.remove_all_passengers()
        for i in range(n):
            self.scroll_to_add_passenger()
            self.common.close_chatbox()
            self.driver.find_element_by_class_name("prenext").click()
    
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
                if placeholder  == "Passenger Name":
                    self.common.close_chatbox()
                    e.clear()
                    e.send_keys(details[i].get("name")[:16].title())
                    
                elif placeholder == "Age":
                    self.common.close_chatbox()
                    e.clear()
                    e.send_keys(details[i].get("age"))
        
        # select dropdown items
        for i, form in enumerate(self.driver.find_elements_by_tag_name("app-passenger")):
            for e in form.find_elements_by_tag_name("select"):
                placeholder = e.get_attribute("formcontrolname")
                e = Select(e)
                if placeholder == "passengerGender":
                    self.common.close_chatbox()
                    e.select_by_visible_text(details[i].get("gender").title())
                    
                elif placeholder == "passengerNationality":
                    self.common.close_chatbox()
                    e.select_by_visible_text(details[i].get("nationality").title())
                    
                elif placeholder == "passengerBerthChoice":
                    self.common.close_chatbox()
                    e.select_by_visible_text(details[i].get("preference").title())
    
    def fill_address(self, address, sleep=0.3):
        for e in self.driver.find_element_by_tag_name("app-address-capture").find_elements_by_tag_name("input"):
            if e.get_attribute("placeholder") == "Correspondence 1 *":
                self.common.close_chatbox()
                e.clear()
                e.send_keys(address.get("city").title())

            elif e.get_attribute("placeholder") == "PIN *":
                self.common.close_chatbox()
                e.clear()
                e.send_keys(address.get("pincode"))

            elif e.get_attribute("placeholder") == "State *":
                self.common.close_chatbox()
                e.click()

        time.sleep(sleep)
        
        self.common.close_chatbox()
        e = Select(self.driver.find_element_by_id("address-City"))
        e.select_by_index(1)
        
        self.common.close_chatbox()
        e = Select(self.driver.find_element_by_id("address-postOffice"))
        e.select_by_index(1)
    
    def fill_number(self, number):
        self.common.close_chatbox()
        self.driver.find_element_by_id("mobileNumber").clear()
        self.driver.find_element_by_id("mobileNumber").send_keys(number)
    
    def fill_details(self, details, sleep=0.1):
        self.fill_passengers(details["passengers"])
        
        time.sleep(sleep)
        self.fill_number(details["mobile"])
        
        time.sleep(sleep)
        self.fill_address({"city": details["city"], "pincode": details["pincode"]})
        
        time.sleep(sleep)
        self.select_insurance(details["travel_insurance"])
        
        time.sleep(sleep)
        self.select_payment_mode(details["payment_mode"])
        
        time.sleep(sleep)
        self.click_submit()
    
    def click_submit(self):
        self.common.close_chatbox()
        self.driver.find_elements_by_class_name("mob-bot-btn")[1].click()
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
                time.sleep(sleep)
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
            self.driver.find_element_by_id("travelInsuranceOptedYes-0").click()
        else:
            self.common.close_chatbox()
            self.driver.find_element_by_id("travelInsuranceOptedNo-0").click()
    
    def select_payment_mode(self, mode):
        payment_modes = {"net_banking": 0, "upi": 1}
        for i, e in enumerate(self.driver.find_elements_by_tag_name("p-radiobutton")[2:]):
            if payment_modes[mode] == i:
                self.driver.execute_script("arguments[0].scrollIntoView();", e)
                self.driver.execute_script("window.scrollBy(0, -300);")
                self.common.close_chatbox()
                e.click()
    
    def is_journey_page(self):
        try:
            return self.driver.find_element_by_tag_name("app-journey-details")
        except: pass
    
    
    def is_payment_page(self):
        return "https://securegw.paytm.in" in self.driver.current_url
    
    def continue_upi_payment(self, upi_id):
        # select bhim upi option
        self.driver.find_element_by_id("pay-type").find_elements_by_class_name("bank-type")[0].click()
        
        # click on continue
        for e in self.driver.find_elements_by_class_name("mob-bot-btn"):
            if e.text == "Continue":
                e.click()
        
        # again select paytm upi
        self.driver.find_elements_by_class_name("bank-text")[1].click()
        
        # click pay & book, this will redirect to payment page
        for e in self.driver.find_elements_by_class_name("mob-bot-btn"):
            if e.text == "Pay & Book":
                e.click()
        
        # wait till payment page is loaded
        while not self.is_payment_page():
            time.sleep(1)
        
        if self.is_payment_page():
            self.fill_paytm_upi(upi_id)
    
    def upi_input_box_visible(self):
        try:
            return self.driver.find_element_by_class_name("pu-title")
        except: pass
            
    def fill_paytm_upi(self, upi_id):
        # fill upi id
        self.driver.find_element_by_id("ptm-upi").click()
        time.sleep(1)

        while not self.upi_input_box_visible():
            time.sleep(1)
        
        # check if enter upi id dialog appeared and fill upi id
        if self.driver.find_element_by_class_name("pu-title"):
            for e in self.driver.find_elements_by_tag_name("input"):
                if e.get_attribute("placeholder") == "username@bank":
                    e.clear()
                    e.send_keys(upi_id)

        time.sleep(.1)
        
        # press pay button
        for e in self.driver.find_elements_by_class_name("btn-primary"):
            if "PAY" in e.text:
                print(e.click())