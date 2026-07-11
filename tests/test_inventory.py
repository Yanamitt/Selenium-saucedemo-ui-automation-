from decimal import Decimal

import pytest

from flows.inventory_flow import InventoryFlow
from test_data.saucedemo import (
    CART_EXPECTED_ADDED_COUNT,
    EXPECTED_INVENTORY_PRODUCT_NAMES,
    INVENTORY_SORT_CASES,
    STANDARD_USER,
)


def price_value(price):
    return Decimal(price.removeprefix("$"))


@pytest.mark.regression
@pytest.mark.inventory
@pytest.mark.parametrize(
    "case",
    INVENTORY_SORT_CASES,
    ids=lambda case: case.case_id,
)
def test_inventory_sort(driver, case):
    result = InventoryFlow(driver).sort_products(STANDARD_USER, case.sort_value)
    values = (
        result.product_names
        if case.field == "name"
        else tuple(price_value(price) for price in result.product_prices)
    )

    assert frozenset(result.product_names) == EXPECTED_INVENTORY_PRODUCT_NAMES
    assert len(result.product_prices) == len(EXPECTED_INVENTORY_PRODUCT_NAMES)
    assert values == tuple(sorted(values, reverse=case.reverse))


@pytest.mark.regression
@pytest.mark.cart
def test_add_and_remove_backpack_updates_cart_badge(driver):
    result = InventoryFlow(driver).toggle_backpack(STANDARD_USER)

    assert result.added_count == CART_EXPECTED_ADDED_COUNT
    assert result.badge_removed is True
