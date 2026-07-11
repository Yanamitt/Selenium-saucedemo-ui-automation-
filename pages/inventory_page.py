from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from base.base_page import BasePage

class InventoryPage(BasePage):
    # Locators
    PAGE_TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    BACKPACK_NAME = (
        By.CSS_SELECTOR,
        "[data-test='item-4-title-link'] [data-test='inventory-item-name']",
    )
    BACKPACK_PRICE = (
        By.XPATH,
        "//*[@data-test='item-4-title-link']"
        "/ancestor::*[@data-test='inventory-item'][1]"
        "//*[@data-test='inventory-item-price']",
    )
    ADD_BACKPACK_BTN = (
        By.CSS_SELECTOR,
        "[data-test='add-to-cart-sauce-labs-backpack']",
    )
    REMOVE_BACKPACK_BTN = (
        By.CSS_SELECTOR,
        "[data-test='remove-sauce-labs-backpack']",
    )
    CART_ICON = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    SORT_SELECT = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    PRODUCT_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    PRODUCT_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")

    def wait_until_loaded(self):
        self.wait_for_url_contains("inventory.html")
        self.wait_for_visibility(self.PAGE_TITLE)
        self.wait_for_clickable(self.CART_ICON)
        return self

    def add_backpack_to_cart(self):
        self.click(self.ADD_BACKPACK_BTN)

    def remove_backpack_from_cart(self):
        self.click(self.REMOVE_BACKPACK_BTN)

    def wait_until_cart_badge_is_empty(self):
        return self.wait_for_invisibility(self.CART_BADGE)

    def go_to_cart(self):
        self.click(self.CART_ICON)

    def sort_products(self, value):
        element = self.wait_for_visibility(self.SORT_SELECT)
        select = Select(element)
        select.select_by_value(value)
        self.wait.until(lambda _: self._sort_is_applied(value))

    def _sort_is_applied(self, value):
        select = Select(self.wait_for_visibility(self.SORT_SELECT))
        selected_value = select.first_selected_option.get_attribute("value")
        if selected_value != value:
            return False

        if value in {"az", "za"}:
            values = self.get_product_names()
        else:
            values = tuple(
                Decimal(price.removeprefix("$")) for price in self.get_product_prices()
            )

        reverse = value in {"za", "hilo"}
        return values == tuple(sorted(values, reverse=reverse))

    def get_product_names(self):
        return tuple(element.text for element in self.wait_for_all_visible(self.PRODUCT_NAMES))

    def get_product_prices(self):
        return tuple(
            element.text for element in self.wait_for_all_visible(self.PRODUCT_PRICES)
        )

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
