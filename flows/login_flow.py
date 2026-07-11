from flows.models import Credentials
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, driver):
        self.driver = driver

    def submit_invalid_login(self, credentials: Credentials) -> str:
        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)
        return login_page.get_error_text()
