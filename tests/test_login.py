import pytest
from pages.login_page import LoginPage


@pytest.mark.parametrize("user, pwd, expected_error", [
    ("locked_out_user", "secret_sauce", "Epic sadface: Sorry, this user has been locked out."),
    ("standard_user", "wrong_pwd", "Epic sadface: Username and password do not match any user in this service"),
    ("", "", "Epic sadface: Username is required")
])
def test_login_failures(driver, user, pwd, expected_error):
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(user, pwd)

    error_text = login_page.get_error_text()
    assert error_text == expected_error
