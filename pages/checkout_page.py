from selenium.webdriver.common.by import By
from base.base_page import BasePage

class CheckoutPage(BasePage):
    # Locators
    FIRST_NAME = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE_BTN = (By.CSS_SELECTOR, "[data-test='continue']")
    FINISH_BTN = (By.CSS_SELECTOR, "[data-test='finish']")
    OVERVIEW_ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    OVERVIEW_ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    SUCCESS_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")

    def wait_until_loaded(self):
        self.wait_for_url_contains("checkout-step-one.html")
        self.wait_for_visibility(self.FIRST_NAME)
        self.wait_for_clickable(self.CONTINUE_BTN)
        return self

    def wait_until_overview_loaded(self):
        self.wait_for_url_contains("checkout-step-two.html")
        self.wait_for_clickable(self.FINISH_BTN)
        return self

    def wait_until_complete_loaded(self):
        self.wait_for_url_contains("checkout-complete.html")
        self.wait_for_visibility(self.SUCCESS_HEADER)
        return self

    def fill_info_and_continue(self, first, last, zip_code):
        self.input_text(self.FIRST_NAME, first)
        self.input_text(self.LAST_NAME, last)
        self.input_text(self.POSTAL_CODE, zip_code)
        self.click(self.CONTINUE_BTN)

    def finish_order(self):
        self.click(self.FINISH_BTN)

    def get_overview_item_name(self):
        return self.get_text(self.OVERVIEW_ITEM_NAME)

    def get_overview_item_price(self):
        return self.get_text(self.OVERVIEW_ITEM_PRICE)

    def get_success_message(self):
        return self.get_text(self.SUCCESS_HEADER)
