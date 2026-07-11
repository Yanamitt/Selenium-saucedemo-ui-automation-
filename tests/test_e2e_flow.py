from flows.shopping_flow import ShoppingFlow
from test_data.saucedemo import (
    BACKPACK_ORDER_EXPECTATION,
    DEFAULT_CHECKOUT_DETAILS,
    STANDARD_USER,
)


def test_saucedemo_e2e_flow(driver):
    result = ShoppingFlow(driver).complete_backpack_order(
        STANDARD_USER,
        DEFAULT_CHECKOUT_DETAILS,
    )
    expected = BACKPACK_ORDER_EXPECTATION

    assert expected.inventory_url_fragment in result.inventory_url
    assert result.page_title == expected.page_title
    assert result.product_name == expected.product_name
    assert result.product_price == expected.product_price
    assert result.cart_count == expected.cart_count

    assert expected.cart_url_fragment in result.cart_url
    assert result.cart_item_name == expected.product_name
    assert result.cart_item_price == expected.product_price

    assert expected.checkout_information_url_fragment in result.checkout_information_url
    assert expected.overview_url_fragment in result.overview_url
    assert result.overview_item_name == expected.product_name
    assert result.overview_item_price == expected.product_price

    assert expected.complete_url_fragment in result.complete_url
    assert result.success_message == expected.success_message, (
        f"预期之外的提示语: {result.success_message}"
    )
