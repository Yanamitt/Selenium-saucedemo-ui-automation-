from flows.models import CartToggleResult, Credentials, InventorySortResult
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class InventoryFlow:
    def __init__(self, driver):
        self.driver = driver

    def _open_inventory(self, credentials: Credentials) -> InventoryPage:
        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)
        return InventoryPage(self.driver).wait_until_loaded()

    def sort_products(
        self,
        credentials: Credentials,
        sort_value: str,
    ) -> InventorySortResult:
        inventory_page = self._open_inventory(credentials)
        inventory_page.sort_products(sort_value)
        return InventorySortResult(
            product_names=inventory_page.get_product_names(),
            product_prices=inventory_page.get_product_prices(),
        )

    def toggle_backpack(self, credentials: Credentials) -> CartToggleResult:
        inventory_page = self._open_inventory(credentials)
        inventory_page.add_backpack_to_cart()
        added_count = inventory_page.get_cart_count()
        inventory_page.remove_backpack_from_cart()
        badge_removed = inventory_page.wait_until_cart_badge_is_empty()
        return CartToggleResult(
            added_count=added_count,
            badge_removed=badge_removed,
        )
