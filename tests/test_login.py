import pytest
from pages.login_page import LoginPage
@pytest.mark.parametrize("user, pwd, expected_error", [
    ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out."),
    ("standard_user", "wrong_pwd", "Username and password do not match"),
    ("", "", "Username is required")
])
def test_login_failures(driver, user, pwd, expected_error):
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(user, pwd)
    
    assert expected_error in login_page.get_error_text()
    error_text = login_page.get_error_text()
    assert "Password is required" not in error_text # 确保不是未输入密码错误
    assert "Username and password do not match" in error_text