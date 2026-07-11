import pytest
from selenium.webdriver.common.by import By

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


EXPECTED_LOCATORS = [
    (LoginPage, "USERNAME_INPUT", (By.CSS_SELECTOR, "[data-test='username']")),
    (LoginPage, "PASSWORD_INPUT", (By.CSS_SELECTOR, "[data-test='password']")),
    (LoginPage, "LOGIN_BTN", (By.CSS_SELECTOR, "[data-test='login-button']")),
    (LoginPage, "ERROR_MESSAGE", (By.CSS_SELECTOR, "[data-test='error']")),
    (InventoryPage, "PAGE_TITLE", (By.CSS_SELECTOR, "[data-test='title']")),
    (
        InventoryPage,
        "BACKPACK_NAME",
        (
            By.CSS_SELECTOR,
            "[data-test='item-4-title-link'] [data-test='inventory-item-name']",
        ),
    ),
    (
        InventoryPage,
        "BACKPACK_PRICE",
        (
            By.XPATH,
            "//*[@data-test='item-4-title-link']"
            "/ancestor::*[@data-test='inventory-item'][1]"
            "//*[@data-test='inventory-item-price']",
        ),
    ),
    (
        InventoryPage,
        "ADD_BACKPACK_BTN",
        (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']"),
    ),
    (
        InventoryPage,
        "REMOVE_BACKPACK_BTN",
        (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']"),
    ),
    (
        InventoryPage,
        "CART_ICON",
        (By.CSS_SELECTOR, "[data-test='shopping-cart-link']"),
    ),
    (
        InventoryPage,
        "CART_BADGE",
        (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']"),
    ),
    (
        InventoryPage,
        "SORT_SELECT",
        (By.CSS_SELECTOR, "[data-test='product-sort-container']"),
    ),
    (
        InventoryPage,
        "PRODUCT_NAMES",
        (By.CSS_SELECTOR, "[data-test='inventory-item-name']"),
    ),
    (
        InventoryPage,
        "PRODUCT_PRICES",
        (By.CSS_SELECTOR, "[data-test='inventory-item-price']"),
    ),
    (CartPage, "ITEM_NAME", (By.CSS_SELECTOR, "[data-test='inventory-item-name']")),
    (CartPage, "ITEM_PRICE", (By.CSS_SELECTOR, "[data-test='inventory-item-price']")),
    (CartPage, "CHECKOUT_BTN", (By.CSS_SELECTOR, "[data-test='checkout']")),
    (CheckoutPage, "FIRST_NAME", (By.CSS_SELECTOR, "[data-test='firstName']")),
    (CheckoutPage, "LAST_NAME", (By.CSS_SELECTOR, "[data-test='lastName']")),
    (CheckoutPage, "POSTAL_CODE", (By.CSS_SELECTOR, "[data-test='postalCode']")),
    (CheckoutPage, "CONTINUE_BTN", (By.CSS_SELECTOR, "[data-test='continue']")),
    (CheckoutPage, "FINISH_BTN", (By.CSS_SELECTOR, "[data-test='finish']")),
    (
        CheckoutPage,
        "OVERVIEW_ITEM_NAME",
        (By.CSS_SELECTOR, "[data-test='inventory-item-name']"),
    ),
    (
        CheckoutPage,
        "OVERVIEW_ITEM_PRICE",
        (By.CSS_SELECTOR, "[data-test='inventory-item-price']"),
    ),
    (
        CheckoutPage,
        "SUCCESS_HEADER",
        (By.CSS_SELECTOR, "[data-test='complete-header']"),
    ),
    (CheckoutPage, "ERROR_MESSAGE", (By.CSS_SELECTOR, "[data-test='error']")),
]


@pytest.mark.parametrize(("page_class", "name", "expected"), EXPECTED_LOCATORS)
def test_page_locator_uses_stable_data_test_contract(page_class, name, expected):
    assert getattr(page_class, name) == expected
