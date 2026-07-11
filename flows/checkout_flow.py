from flows.models import CheckoutDetails, CheckoutValidationResult, Credentials
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class CheckoutFlow:
    def __init__(self, driver):
        self.driver = driver

    def submit_invalid_information(
        self,
        credentials: Credentials,
        details: CheckoutDetails,
    ) -> CheckoutValidationResult:
        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)

        inventory_page = InventoryPage(self.driver).wait_until_loaded()
        inventory_page.add_backpack_to_cart()
        inventory_page.go_to_cart()

        cart_page = CartPage(self.driver).wait_until_loaded()
        cart_page.proceed_to_checkout()

        checkout_page = CheckoutPage(self.driver).wait_until_loaded()
        checkout_page.fill_info_and_continue(
            details.first_name,
            details.last_name,
            details.postal_code,
        )
        return CheckoutValidationResult(
            checkout_url=checkout_page.current_url(),
            error_message=checkout_page.get_error_text(),
        )
