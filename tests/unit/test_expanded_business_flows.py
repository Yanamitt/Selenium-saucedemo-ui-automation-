from unittest.mock import Mock, call

from flows.checkout_flow import CheckoutFlow
from flows.inventory_flow import InventoryFlow
from flows.login_flow import LoginFlow
from flows.models import (
    CartToggleResult,
    CheckoutDetails,
    CheckoutValidationResult,
    Credentials,
    InventorySortResult,
    LoginSuccessResult,
)


def attach_calls(*entries):
    timeline = Mock()
    for name, tracked_mock in entries:
        timeline.attach_mock(tracked_mock, name)
    return timeline


def test_login_flow_returns_successful_inventory_observations(monkeypatch):
    driver = object()
    credentials = Credentials("standard_user", "secret_sauce")
    login_page = Mock()
    inventory_page = Mock()
    inventory_page.wait_until_loaded.return_value = inventory_page
    inventory_page.current_url.return_value = "https://example.test/inventory.html"
    inventory_page.get_page_title.return_value = "Products"
    login_factory = Mock(return_value=login_page)
    inventory_factory = Mock(return_value=inventory_page)
    monkeypatch.setattr("flows.login_flow.LoginPage", login_factory)
    monkeypatch.setattr("flows.login_flow.InventoryPage", inventory_factory)
    timeline = attach_calls(
        ("login_page", login_factory),
        ("load", login_page.load),
        ("login", login_page.login),
        ("inventory_page", inventory_factory),
        ("wait_inventory", inventory_page.wait_until_loaded),
        ("inventory_url", inventory_page.current_url),
        ("page_title", inventory_page.get_page_title),
    )

    result = LoginFlow(driver).submit_valid_login(credentials)

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load(),
        call.login("standard_user", "secret_sauce"),
        call.inventory_page(driver),
        call.wait_inventory(),
        call.inventory_url(),
        call.page_title(),
    ]
    assert result == LoginSuccessResult(
        inventory_url="https://example.test/inventory.html",
        page_title="Products",
    )


def test_inventory_flow_sorts_and_returns_visible_products(monkeypatch):
    driver = object()
    credentials = Credentials("standard_user", "secret_sauce")
    login_page = Mock()
    inventory_page = Mock()
    inventory_page.wait_until_loaded.return_value = inventory_page
    inventory_page.get_product_names.return_value = ("Bike Light", "Backpack")
    inventory_page.get_product_prices.return_value = ("$9.99", "$29.99")
    login_factory = Mock(return_value=login_page)
    inventory_factory = Mock(return_value=inventory_page)
    monkeypatch.setattr("flows.inventory_flow.LoginPage", login_factory)
    monkeypatch.setattr("flows.inventory_flow.InventoryPage", inventory_factory)
    timeline = attach_calls(
        ("login_page", login_factory),
        ("load", login_page.load),
        ("login", login_page.login),
        ("inventory_page", inventory_factory),
        ("wait_inventory", inventory_page.wait_until_loaded),
        ("sort", inventory_page.sort_products),
        ("names", inventory_page.get_product_names),
        ("prices", inventory_page.get_product_prices),
    )

    result = InventoryFlow(driver).sort_products(credentials, "lohi")

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load(),
        call.login("standard_user", "secret_sauce"),
        call.inventory_page(driver),
        call.wait_inventory(),
        call.sort("lohi"),
        call.names(),
        call.prices(),
    ]
    assert result == InventorySortResult(
        product_names=("Bike Light", "Backpack"),
        product_prices=("$9.99", "$29.99"),
    )


def test_inventory_flow_adds_and_removes_backpack(monkeypatch):
    driver = object()
    credentials = Credentials("standard_user", "secret_sauce")
    login_page = Mock()
    inventory_page = Mock()
    inventory_page.wait_until_loaded.return_value = inventory_page
    inventory_page.get_cart_count.return_value = "1"
    inventory_page.wait_until_cart_badge_is_empty.return_value = True
    login_factory = Mock(return_value=login_page)
    inventory_factory = Mock(return_value=inventory_page)
    monkeypatch.setattr("flows.inventory_flow.LoginPage", login_factory)
    monkeypatch.setattr("flows.inventory_flow.InventoryPage", inventory_factory)
    timeline = attach_calls(
        ("login_page", login_factory),
        ("load", login_page.load),
        ("login", login_page.login),
        ("inventory_page", inventory_factory),
        ("wait_inventory", inventory_page.wait_until_loaded),
        ("add", inventory_page.add_backpack_to_cart),
        ("cart_count", inventory_page.get_cart_count),
        ("remove", inventory_page.remove_backpack_from_cart),
        ("wait_empty", inventory_page.wait_until_cart_badge_is_empty),
    )

    result = InventoryFlow(driver).toggle_backpack(credentials)

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load(),
        call.login("standard_user", "secret_sauce"),
        call.inventory_page(driver),
        call.wait_inventory(),
        call.add(),
        call.cart_count(),
        call.remove(),
        call.wait_empty(),
    ]
    assert result == CartToggleResult(added_count="1", badge_removed=True)


def test_checkout_flow_returns_required_field_error(monkeypatch):
    driver = object()
    credentials = Credentials("standard_user", "secret_sauce")
    details = CheckoutDetails("", "", "")
    login_page = Mock()
    inventory_page = Mock()
    cart_page = Mock()
    checkout_page = Mock()
    inventory_page.wait_until_loaded.return_value = inventory_page
    cart_page.wait_until_loaded.return_value = cart_page
    checkout_page.wait_until_loaded.return_value = checkout_page
    checkout_page.current_url.return_value = (
        "https://example.test/checkout-step-one.html"
    )
    checkout_page.get_error_text.return_value = "Error: First Name is required"
    login_factory = Mock(return_value=login_page)
    inventory_factory = Mock(return_value=inventory_page)
    cart_factory = Mock(return_value=cart_page)
    checkout_factory = Mock(return_value=checkout_page)
    monkeypatch.setattr("flows.checkout_flow.LoginPage", login_factory)
    monkeypatch.setattr("flows.checkout_flow.InventoryPage", inventory_factory)
    monkeypatch.setattr("flows.checkout_flow.CartPage", cart_factory)
    monkeypatch.setattr("flows.checkout_flow.CheckoutPage", checkout_factory)
    timeline = attach_calls(
        ("login_page", login_factory),
        ("load", login_page.load),
        ("login", login_page.login),
        ("inventory_page", inventory_factory),
        ("wait_inventory", inventory_page.wait_until_loaded),
        ("add", inventory_page.add_backpack_to_cart),
        ("go_to_cart", inventory_page.go_to_cart),
        ("cart_page", cart_factory),
        ("wait_cart", cart_page.wait_until_loaded),
        ("proceed", cart_page.proceed_to_checkout),
        ("checkout_page", checkout_factory),
        ("wait_checkout", checkout_page.wait_until_loaded),
        ("fill", checkout_page.fill_info_and_continue),
        ("checkout_url", checkout_page.current_url),
        ("error", checkout_page.get_error_text),
    )

    result = CheckoutFlow(driver).submit_invalid_information(credentials, details)

    assert timeline.mock_calls == [
        call.login_page(driver),
        call.load(),
        call.login("standard_user", "secret_sauce"),
        call.inventory_page(driver),
        call.wait_inventory(),
        call.add(),
        call.go_to_cart(),
        call.cart_page(driver),
        call.wait_cart(),
        call.proceed(),
        call.checkout_page(driver),
        call.wait_checkout(),
        call.fill("", "", ""),
        call.checkout_url(),
        call.error(),
    ]
    assert result == CheckoutValidationResult(
        checkout_url="https://example.test/checkout-step-one.html",
        error_message="Error: First Name is required",
    )
