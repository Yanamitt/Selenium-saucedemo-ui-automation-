from unittest.mock import Mock, call

from flows.login_flow import LoginFlow
from flows.models import CheckoutDetails, Credentials, ShoppingFlowResult
from flows.shopping_flow import ShoppingFlow


def test_login_flow_submits_credentials_and_returns_error(monkeypatch):
    driver = object()
    credentials = Credentials("locked_out_user", "secret_sauce")
    login_page = Mock()
    login_page.load.return_value = login_page
    login_page.get_error_text.return_value = "locked out"
    page_factory = Mock(return_value=login_page)
    monkeypatch.setattr("flows.login_flow.LoginPage", page_factory)
    timeline = Mock()
    timeline.attach_mock(page_factory, "login_page")
    timeline.attach_mock(login_page.load, "load")
    timeline.attach_mock(login_page.login, "login")
    timeline.attach_mock(login_page.get_error_text, "get_error_text")

    error_text = LoginFlow(driver).submit_invalid_login(credentials)

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load(),
        call.login("locked_out_user", "secret_sauce"),
        call.get_error_text(),
    ]
    assert error_text == "locked out"


def test_shopping_flow_returns_observations_without_asserting_them(monkeypatch):
    driver = object()
    credentials = Credentials("standard_user", "secret_sauce")
    checkout_details = CheckoutDetails("Test", "User", "12345")

    login_page = Mock()
    inventory_page = Mock()
    cart_page = Mock()
    checkout_page = Mock()

    inventory_page.wait_until_loaded.return_value = inventory_page
    inventory_page.current_url.return_value = "https://example.test/inventory.html"
    inventory_page.get_page_title.return_value = "Products"
    inventory_page.get_backpack_name.return_value = "Sauce Labs Backpack"
    inventory_page.get_backpack_price.return_value = "$29.99"
    inventory_page.get_cart_count.return_value = "1"

    cart_page.wait_until_loaded.return_value = cart_page
    cart_page.current_url.return_value = "https://example.test/cart.html"
    cart_page.get_item_name.return_value = "Sauce Labs Backpack"
    cart_page.get_item_price.return_value = "$29.99"

    checkout_page.wait_until_loaded.return_value = checkout_page
    checkout_page.wait_until_overview_loaded.return_value = checkout_page
    checkout_page.wait_until_complete_loaded.return_value = checkout_page
    checkout_page.current_url.side_effect = [
        "https://example.test/checkout-step-one.html",
        "https://example.test/checkout-step-two.html",
        "https://example.test/checkout-complete.html",
    ]
    checkout_page.get_overview_item_name.return_value = "Sauce Labs Backpack"
    checkout_page.get_overview_item_price.return_value = "$29.99"
    checkout_page.get_success_message.return_value = "Thank you for your order!"

    login_factory = Mock(return_value=login_page)
    inventory_factory = Mock(return_value=inventory_page)
    cart_factory = Mock(return_value=cart_page)
    checkout_factory = Mock(return_value=checkout_page)
    monkeypatch.setattr("flows.shopping_flow.LoginPage", login_factory)
    monkeypatch.setattr("flows.shopping_flow.InventoryPage", inventory_factory)
    monkeypatch.setattr("flows.shopping_flow.CartPage", cart_factory)
    monkeypatch.setattr("flows.shopping_flow.CheckoutPage", checkout_factory)

    timeline = Mock()
    tracked_calls = (
        (login_factory, "login_page"),
        (login_page.load, "load_login"),
        (login_page.login, "login"),
        (inventory_factory, "inventory_page"),
        (inventory_page.wait_until_loaded, "wait_inventory"),
        (inventory_page.current_url, "inventory_url"),
        (inventory_page.get_page_title, "page_title"),
        (inventory_page.get_backpack_name, "product_name"),
        (inventory_page.get_backpack_price, "product_price"),
        (inventory_page.add_backpack_to_cart, "add_to_cart"),
        (inventory_page.get_cart_count, "cart_count"),
        (inventory_page.go_to_cart, "go_to_cart"),
        (cart_factory, "cart_page"),
        (cart_page.wait_until_loaded, "wait_cart"),
        (cart_page.current_url, "cart_url"),
        (cart_page.get_item_name, "cart_item_name"),
        (cart_page.get_item_price, "cart_item_price"),
        (cart_page.proceed_to_checkout, "proceed_to_checkout"),
        (checkout_factory, "checkout_page"),
        (checkout_page.wait_until_loaded, "wait_checkout_information"),
        (checkout_page.current_url, "checkout_url"),
        (checkout_page.fill_info_and_continue, "fill_checkout_information"),
        (checkout_page.wait_until_overview_loaded, "wait_overview"),
        (checkout_page.get_overview_item_name, "overview_item_name"),
        (checkout_page.get_overview_item_price, "overview_item_price"),
        (checkout_page.finish_order, "finish_order"),
        (checkout_page.wait_until_complete_loaded, "wait_complete"),
        (checkout_page.get_success_message, "success_message"),
    )
    for tracked_mock, name in tracked_calls:
        timeline.attach_mock(tracked_mock, name)

    result = ShoppingFlow(driver).complete_backpack_order(
        credentials,
        checkout_details,
    )

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load_login(),
        call.login("standard_user", "secret_sauce"),
        call.inventory_page(driver),
        call.wait_inventory(),
        call.inventory_url(),
        call.page_title(),
        call.product_name(),
        call.product_price(),
        call.add_to_cart(),
        call.cart_count(),
        call.go_to_cart(),
        call.cart_page(driver),
        call.wait_cart(),
        call.cart_url(),
        call.cart_item_name(),
        call.cart_item_price(),
        call.proceed_to_checkout(),
        call.checkout_page(driver),
        call.wait_checkout_information(),
        call.checkout_url(),
        call.fill_checkout_information("Test", "User", "12345"),
        call.wait_overview(),
        call.checkout_url(),
        call.overview_item_name(),
        call.overview_item_price(),
        call.finish_order(),
        call.wait_complete(),
        call.checkout_url(),
        call.success_message(),
    ]
    assert result == ShoppingFlowResult(
        inventory_url="https://example.test/inventory.html",
        page_title="Products",
        product_name="Sauce Labs Backpack",
        product_price="$29.99",
        cart_count="1",
        cart_url="https://example.test/cart.html",
        cart_item_name="Sauce Labs Backpack",
        cart_item_price="$29.99",
        checkout_information_url="https://example.test/checkout-step-one.html",
        overview_url="https://example.test/checkout-step-two.html",
        overview_item_name="Sauce Labs Backpack",
        overview_item_price="$29.99",
        complete_url="https://example.test/checkout-complete.html",
        success_message="Thank you for your order!",
    )
