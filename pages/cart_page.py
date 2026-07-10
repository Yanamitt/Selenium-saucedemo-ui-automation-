from selenium.webdriver.common.by import By
from base.base_page import BasePage

class CartPage(BasePage):
    ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    CHECKOUT_BTN = (By.ID, "checkout")

    def get_item_name(self):
        return self.get_text(self.ITEM_NAME)

    def get_item_price(self):
        return self.get_text(self.ITEM_PRICE)

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BTN)
