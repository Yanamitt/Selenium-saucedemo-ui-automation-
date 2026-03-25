from selenium.webdriver.common.by import By
from base.base_page import BasePage

class LoginPage(BasePage):
    URL = "https://www.saucedemo.com/"
    
    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']") # 错误提示框

    def load(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)
    def get_error_text(self):
        """获取登录失败时的错误提示"""
        return self.get_text(self.ERROR_MESSAGE)    