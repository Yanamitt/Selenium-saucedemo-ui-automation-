import pytest

from flows.login_flow import LoginFlow
from test_data.saucedemo import STANDARD_LOGIN_EXPECTATION, STANDARD_USER


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.login
def test_standard_user_login_success(driver):
    result = LoginFlow(driver).submit_valid_login(STANDARD_USER)

    assert STANDARD_LOGIN_EXPECTATION.inventory_url_fragment in result.inventory_url
    assert result.page_title == STANDARD_LOGIN_EXPECTATION.page_title
