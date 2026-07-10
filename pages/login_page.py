from selenium.webdriver.common.by import By
from base.base_page import BasePage
from settings import DEFAULT_BASE_URL, get_base_url


class LoginPage(BasePage):
    URL = DEFAULT_BASE_URL

    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")

    def load(self):
        self.driver.get(get_base_url())

    def login(self, username, password):
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def get_error_text(self):
        """获取登录失败时的错误提示"""
        return self.get_text(self.ERROR_MESSAGE)
