from selenium.webdriver.common.by import By
from base.base_page import BasePage
from settings import DEFAULT_BASE_URL, get_base_url


class LoginPage(BasePage):
    URL = DEFAULT_BASE_URL

    # Locators
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def wait_until_loaded(self):
        self.wait_for_url_contains(get_base_url())
        self.wait_for_visibility(self.USERNAME_INPUT)
        self.wait_for_clickable(self.LOGIN_BTN)
        return self

    def load(self):
        self.driver.get(get_base_url())
        return self.wait_until_loaded()

    def login(self, username, password):
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def get_error_text(self):
        """获取登录失败时的错误提示"""
        return self.get_text(self.ERROR_MESSAGE)
