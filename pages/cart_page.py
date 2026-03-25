from selenium.webdriver.common.by import By
from base.base_page import BasePage

class CartPage(BasePage):
    CHECKOUT_BTN = (By.ID, "checkout")

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BTN)