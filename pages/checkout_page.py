from selenium.webdriver.common.by import By
from base.base_page import BasePage

class CheckoutPage(BasePage):
    # Locators
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BTN = (By.ID, "continue")
    FINISH_BTN = (By.ID, "finish")
    OVERVIEW_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    OVERVIEW_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    SUCCESS_HEADER = (By.CLASS_NAME, "complete-header")

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
