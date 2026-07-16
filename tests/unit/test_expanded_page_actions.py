from unittest.mock import Mock

from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage


def make_page(page_class):
    return page_class.__new__(page_class)


def test_inventory_sort_selects_requested_value(monkeypatch):
    page = make_page(InventoryPage)
    select_element = object()
    refreshed_select_element = object()
    page.wait_for_visibility = Mock(
        side_effect=[select_element, refreshed_select_element]
    )
    page.wait = Mock()
    select = Mock()
    refreshed_select = Mock()
    refreshed_select.first_selected_option.get_attribute.return_value = "lohi"
    select_factory = Mock(side_effect=[select, refreshed_select])
    monkeypatch.setattr("pages.inventory_page.Select", select_factory)
    page.get_product_prices = Mock(return_value=("$9.99", "$29.99"))

    page.sort_products("lohi")

    select.select_by_value.assert_called_once_with("lohi")
    page.wait.until.assert_called_once()
    condition = page.wait.until.call_args.args[0]
    assert condition(None) is True
    assert page.wait_for_visibility.call_args_list == [
        ((page.SORT_SELECT,),),
        ((page.SORT_SELECT,),),
    ]
    assert select_factory.call_args_list == [
        ((select_element,),),
        ((refreshed_select_element,),),
    ]


def test_inventory_returns_all_visible_product_names_and_prices():
    page = make_page(InventoryPage)
    page.wait_for_all_visible = Mock(
        side_effect=[
            [Mock(text="Backpack"), Mock(text="Bike Light")],
            [Mock(text="$29.99"), Mock(text="$9.99")],
        ]
    )

    names = page.get_product_names()
    prices = page.get_product_prices()

    assert names == ("Backpack", "Bike Light")
    assert prices == ("$29.99", "$9.99")
    assert page.wait_for_all_visible.call_args_list == [
        ((page.PRODUCT_NAMES,),),
        ((page.PRODUCT_PRICES,),),
    ]


def test_inventory_removes_backpack_and_waits_for_empty_badge():
    page = make_page(InventoryPage)
    page.click = Mock()
    page.wait_for_invisibility = Mock(return_value=True)

    page.remove_backpack_from_cart()
    badge_removed = page.wait_until_cart_badge_is_empty()

    page.click.assert_called_once_with(page.REMOVE_BACKPACK_BTN)
    page.wait_for_invisibility.assert_called_once_with(page.CART_BADGE)
    assert badge_removed is True


def test_checkout_returns_validation_error_text():
    page = make_page(CheckoutPage)
    page.get_text = Mock(return_value="Error: First Name is required")

    assert page.get_error_text() == "Error: First Name is required"
    page.get_text.assert_called_once_with(page.ERROR_MESSAGE)
