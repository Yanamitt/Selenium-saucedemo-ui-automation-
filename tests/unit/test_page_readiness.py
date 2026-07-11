from unittest.mock import Mock, call

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def make_page(page_class):
    page = page_class.__new__(page_class)
    page.driver = Mock()
    page.readiness_calls = Mock()
    for method_name in (
        "wait_for_url_contains",
        "wait_for_visibility",
        "wait_for_clickable",
    ):
        method = Mock()
        setattr(page, method_name, method)
        page.readiness_calls.attach_mock(method, method_name)
    return page


def test_login_page_waits_for_url_and_login_controls(monkeypatch):
    page = make_page(LoginPage)
    base_url = "https://example.test/"
    monkeypatch.setattr("pages.login_page.get_base_url", Mock(return_value=base_url))

    result = page.wait_until_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains(base_url),
        call.wait_for_visibility(page.USERNAME_INPUT),
        call.wait_for_clickable(page.LOGIN_BTN),
    ]


def test_login_page_loads_configured_url_and_waits_until_ready(monkeypatch):
    page = make_page(LoginPage)
    base_url = "https://example.test/"
    monkeypatch.setattr("pages.login_page.get_base_url", Mock(return_value=base_url))
    page.wait_until_loaded = Mock(return_value=page)
    load_calls = Mock()
    load_calls.attach_mock(page.driver.get, "get")
    load_calls.attach_mock(page.wait_until_loaded, "wait_until_loaded")

    result = page.load()

    assert result is page
    assert load_calls.mock_calls == [
        call.get(base_url),
        call.wait_until_loaded(),
    ]


def test_inventory_page_waits_for_url_title_and_primary_action():
    page = make_page(InventoryPage)

    result = page.wait_until_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains("inventory.html"),
        call.wait_for_visibility(page.PAGE_TITLE),
        call.wait_for_clickable(page.CART_ICON),
    ]


def test_cart_page_waits_for_url_and_checkout_action():
    page = make_page(CartPage)

    result = page.wait_until_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains("cart.html"),
        call.wait_for_clickable(page.CHECKOUT_BTN),
    ]


def test_checkout_page_waits_for_information_step():
    page = make_page(CheckoutPage)

    result = page.wait_until_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains("checkout-step-one.html"),
        call.wait_for_visibility(page.FIRST_NAME),
        call.wait_for_clickable(page.CONTINUE_BTN),
    ]


def test_checkout_page_waits_for_overview_step():
    page = make_page(CheckoutPage)

    result = page.wait_until_overview_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains("checkout-step-two.html"),
        call.wait_for_clickable(page.FINISH_BTN),
    ]


def test_checkout_page_waits_for_complete_step():
    page = make_page(CheckoutPage)

    result = page.wait_until_complete_loaded()

    assert result is page
    assert page.readiness_calls.mock_calls == [
        call.wait_for_url_contains("checkout-complete.html"),
        call.wait_for_visibility(page.SUCCESS_HEADER),
    ]
