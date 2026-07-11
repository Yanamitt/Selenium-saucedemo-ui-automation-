import pytest

from flows.login_flow import LoginFlow
from test_data.saucedemo import LOGIN_FAILURE_CASES


@pytest.mark.parametrize(
    "case",
    LOGIN_FAILURE_CASES,
    ids=lambda case: case.case_id,
)
def test_login_failures(driver, case):
    error_text = LoginFlow(driver).submit_invalid_login(case.credentials)

    assert error_text == case.expected_error
