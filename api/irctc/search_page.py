import time
from .common import Common

class Slot:
    def __init__(self, driver, e, book_now_button, train_idx):
        self.driver = driver
        self.e = e
        self.book_now_button = book_now_button
        self.train_idx = train_idx
        
        self.repr = self.e.text.replace("\n", ", ").lower()
        self.weekday = self.repr.split(", ")[0]
        self.day = int(self.repr.split(", ")[1].split(" ")[0])
        self.month = self.repr.split(", ")[1].split(" ")[1]
        self.fare = ""
    
    def __repr__(self):
        return self.repr.replace(" ", "-").replace(",", "")
    
    def select_date(self):
        self.e.click()
        self.wait_until_loaded()
        
        # get fare
        idx = 0
        for e in self.driver.find_elements_by_tag_name("app-train-avl-enq"):
            if idx == self.train_idx:
                for s in e.find_elements_by_tag_name("strong"):
                    if "₹" in s.text:
                        self.fare = s.text
                        break
                break
            if e.text: idx +=1
    
    @property
    def loading(self, sleep=0.3):
        try:
            time.sleep(sleep)
            self.driver.find_element_by_class_name("loading-bg")
            return True
        except:
            return False
    
    def wait_until_loaded(self, sleep=0.03):
        while self.loading:
            time.sleep(sleep)
        
    def bypass_confirmation(self):
        try:
            # bypass the confirmation box, if appear
            if self.driver.find_element_by_class_name("ui-dialog-title"):
                self.driver.find_element_by_class_name("ui-button-text").click()
        except Exception as e: pass
    
    def book_now(self, sleep=0.1):
        self.select_date()
        time.sleep(sleep)
        
        self.book_now_button.click()
        time.sleep(sleep)
        
        self.bypass_confirmation()
        time.sleep(sleep)
        
        self.bypass_confirmation()
        self.wait_until_loaded()
        time.sleep(1)


class SearchPage:
    def __init__(self, driver, login_page, booking_page):
        self.driver = driver
        self.login_page = login_page
        self.booking_page = booking_page
        self.common = Common(driver)
    
    def search_train(self, details):
        # details = {
        #     "origin": "MFP",
        #     "destination": "NDLS",
        #     "date": "16/01/2022",
        #     "class": "SL",
        #     "quota": "TATKAL",
        #     "train_number": "12553",
        #     "options": {
        #         "divyaang_concession": False,
        #         "flexible_with_date": False,
        #         "train_with_available_berth": False,
        #         "railway_pass_concession": False
        #     }
        # }
        
        if self.booking_page.booking_tab_visible:
            self.booking_page.fill_origin(details['origin'])
            self.booking_page.fill_destination(details['destination'])
            self.booking_page.fill_date(details['date'])
            self.booking_page.fill_class(details['class'])
            self.booking_page.fill_quota(details['quota'])
            
            if details.get('options', None):
                self.booking_page.select_checkboxes(details.get('options', {}))
            
            self.booking_page.click_search()
            self.booking_page.wait_until_loaded()
            
            if self.booking_page.error_toast:
                return self.booking_page.error_toast
            elif self.booking_page.train_list_page_visible:
                return self.get_train_details(details['train_number'], details['class'])
            else:
                return "unable to find train"
        
        elif self.booking_page.train_list_page_visible:
            for i in range(6):
                # go back multiple times
                self.booking_page.go_back()
                self.common.sleep(0.1)
            
            self.common.sleep(0.1)
            return self.search_train(details)
    
    def get_train_details(self, train_number, train_class):
        train_idx = None
        for (i, e) in enumerate(self.driver.find_elements_by_class_name("train-heading")):
            if f"({train_number})" in e.text:
                train_idx = i
        
        if train_idx is None: return False
        
        idx = 0
        for e in self.driver.find_elements_by_tag_name("table"):
            if idx == train_idx:
                try:
                    # click on refresh train button
                    refresh_button = e.find_element_by_class_name("fa-repeat")
                    self.driver.execute_script("return arguments[0].scrollIntoView();", e)
                    self.driver.execute_script("window.scrollBy(0, -150);")
                    refresh_button.click()
                    self.booking_page.wait_until_loaded()
                    
                    # check if there's any error while fetching train details
                    if self.booking_page.error_toast:
                        return self.booking_page.error_toast
                except: pass

                class_found = False
                # iterate through train classes i.e 2S, SL, 3A, etc.
                for li in self.driver.find_element_by_tag_name("p-tabmenu").find_elements_by_tag_name("li"):
                    if li.text == train_class:
                        class_found = True
                        if li.get_attribute("aria-selected") == "false":
                            # select preferred train class
                            li.click(); self.booking_page.wait_until_loaded()
                        break
                
                if class_found:
                    jdx = 0
                    slots = []
                    for e in self.driver.find_elements_by_tag_name("table"):
                        if jdx == train_idx:
                            for td in e.find_elements_by_tag_name("td"):
                                if not td.text: continue
                                if "TRAIN CANCELLED" in td.text: continue
                                
                                book_now_button = self.find_book_now_button(train_idx)
                                slots.append(Slot(self.driver, td, book_now_button, train_idx))
                                
                            return slots
                        if e.text: jdx += 1

                break
            if e.text: idx += 1
        return []
    
    def find_book_now_button(self, train_idx):
        idx = 0
        for e in self.driver.find_elements_by_tag_name("app-train-avl-enq"):
            if idx == train_idx:
                return e.find_element_by_tag_name("button")
            if e.text: idx +=1