import logging

from flows.models import CheckoutDetails, Credentials, ShoppingFlowResult
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


logger = logging.getLogger(__name__)


class ShoppingFlow:
    def __init__(self, driver):
        self.driver = driver

    def complete_backpack_order(
        self,
        credentials: Credentials,
        checkout_details: CheckoutDetails,
    ) -> ShoppingFlowResult:
        logger.info("开始测试：SauceDemo 核心购物流程")

        login_page = LoginPage(self.driver)
        login_page.load()
        login_page.login(credentials.username, credentials.password)

        inventory_page = InventoryPage(self.driver).wait_until_loaded()
        inventory_url = inventory_page.current_url()
        page_title = inventory_page.get_page_title()
        product_name = inventory_page.get_backpack_name()
        product_price = inventory_page.get_backpack_price()
        logger.info("步骤 1：登录成功")

        inventory_page.add_backpack_to_cart()
        cart_count = inventory_page.get_cart_count()
        inventory_page.go_to_cart()

        cart_page = CartPage(self.driver).wait_until_loaded()
        cart_url = cart_page.current_url()
        cart_item_name = cart_page.get_item_name()
        cart_item_price = cart_page.get_item_price()
        logger.info("步骤 2：商品已添加至购物车")

        cart_page.proceed_to_checkout()
        checkout_page = CheckoutPage(self.driver).wait_until_loaded()
        checkout_information_url = checkout_page.current_url()
        logger.info("步骤 3：进入结算页面")

        checkout_page.fill_info_and_continue(
            checkout_details.first_name,
            checkout_details.last_name,
            checkout_details.postal_code,
        )
        checkout_page.wait_until_overview_loaded()
        overview_url = checkout_page.current_url()
        overview_item_name = checkout_page.get_overview_item_name()
        overview_item_price = checkout_page.get_overview_item_price()

        checkout_page.finish_order()
        checkout_page.wait_until_complete_loaded()
        complete_url = checkout_page.current_url()
        success_message = checkout_page.get_success_message()
        logger.info("步骤 4：订单提交完成")

        return ShoppingFlowResult(
            inventory_url=inventory_url,
            page_title=page_title,
            product_name=product_name,
            product_price=product_price,
            cart_count=cart_count,
            cart_url=cart_url,
            cart_item_name=cart_item_name,
            cart_item_price=cart_item_price,
            checkout_information_url=checkout_information_url,
            overview_url=overview_url,
            overview_item_name=overview_item_name,
            overview_item_price=overview_item_price,
            complete_url=complete_url,
            success_message=success_message,
        )
