from flows.models import Credentials, LoginSuccessResult
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, driver):
        self.driver = driver

    def submit_invalid_login(self, credentials: Credentials) -> str:
        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)
        return login_page.get_error_text()

    def submit_valid_login(self, credentials: Credentials) -> LoginSuccessResult:
        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)
        inventory_page = InventoryPage(self.driver).wait_until_loaded()
        return LoginSuccessResult(
            inventory_url=inventory_page.current_url(),
            page_title=inventory_page.get_page_title(),
        )
