from selenium.webdriver.common.by import By
from base.base_page import BasePage

class CartPage(BasePage):
    ITEM_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    CHECKOUT_BTN = (By.CSS_SELECTOR, "[data-test='checkout']")

    def wait_until_loaded(self):
        self.wait_for_url_contains("cart.html")
        self.wait_for_clickable(self.CHECKOUT_BTN)
        return self

    def get_item_name(self):
        return self.get_text(self.ITEM_NAME)

    def get_item_price(self):
        return self.get_text(self.ITEM_PRICE)

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BTN)
