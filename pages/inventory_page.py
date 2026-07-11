from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from base.base_page import BasePage

class InventoryPage(BasePage):
    # Locators
    PAGE_TITLE = (By.CLASS_NAME, "title")
    BACKPACK_NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    BACKPACK_PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ADD_BACKPACK_BTN = (By.ID, "add-to-cart-sauce-labs-backpack")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    def wait_until_loaded(self):
        self.wait_for_url_contains("inventory.html")
        self.wait_for_visibility(self.PAGE_TITLE)
        self.wait_for_clickable(self.CART_ICON)
        return self

    def add_backpack_to_cart(self):
        self.click(self.ADD_BACKPACK_BTN)

    def go_to_cart(self):
        self.click(self.CART_ICON)

    def get_page_title(self):
        return self.get_text(self.PAGE_TITLE)

    def get_backpack_name(self):
        return self.get_text(self.BACKPACK_NAME)

    def get_backpack_price(self):
        return self.get_text(self.BACKPACK_PRICE)

    def get_cart_count(self):
        try:
            return self.get_text(self.CART_BADGE)
        except TimeoutException:
            return "0"
