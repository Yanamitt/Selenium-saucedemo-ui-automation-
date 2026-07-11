import pytest

from flows.checkout_flow import CheckoutFlow
from test_data.saucedemo import (
    CHECKOUT_INFORMATION_URL_FRAGMENT,
    CHECKOUT_VALIDATION_CASES,
    STANDARD_USER,
)


@pytest.mark.regression
@pytest.mark.checkout
@pytest.mark.parametrize(
    "case",
    CHECKOUT_VALIDATION_CASES,
    ids=lambda case: case.case_id,
)
def test_checkout_required_fields(driver, case):
    result = CheckoutFlow(driver).submit_invalid_information(
        STANDARD_USER,
        case.details,
    )

    assert CHECKOUT_INFORMATION_URL_FRAGMENT in result.checkout_url
    assert result.error_message == case.expected_error
