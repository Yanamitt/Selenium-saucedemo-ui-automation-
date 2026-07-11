from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
import logging

def test_saucedemo_e2e_flow(driver):
    logging.info("开始测试：SauceDemo 核心购物流程")

    # 1. 登录
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(driver).wait_until_loaded()
    assert "inventory.html" in driver.current_url
    logging.info("步骤 1：登录成功")

    # 2. 浏览并添加商品
    assert inventory_page.get_page_title() == "Products"
    product_name = inventory_page.get_backpack_name()
    product_price = inventory_page.get_backpack_price()
    assert product_name == "Sauce Labs Backpack"
    assert product_price == "$29.99"

    inventory_page.add_backpack_to_cart()
    assert inventory_page.get_cart_count() == "1"
    inventory_page.go_to_cart()
    cart_page = CartPage(driver).wait_until_loaded()
    logging.info("步骤 2：商品已添加至购物车")

    # 3. 购物车确认
    assert "cart.html" in driver.current_url
    assert cart_page.get_item_name() == product_name
    assert cart_page.get_item_price() == product_price
    cart_page.proceed_to_checkout()
    checkout_page = CheckoutPage(driver).wait_until_loaded()
    assert "checkout-step-one.html" in driver.current_url
    logging.info("步骤 3：进入结算页面")

    # 4. 填写信息并下单
    checkout_page.fill_info_and_continue("Test", "User", "12345")
    checkout_page.wait_until_overview_loaded()
    assert "checkout-step-two.html" in driver.current_url
    assert checkout_page.get_overview_item_name() == product_name
    assert checkout_page.get_overview_item_price() == product_price
    checkout_page.finish_order()
    checkout_page.wait_until_complete_loaded()
    assert "checkout-complete.html" in driver.current_url
    logging.info("步骤 4：订单提交完成")

    # 5. 断言验证
    success_msg = checkout_page.get_success_message()
    assert success_msg == "Thank you for your order!", f"预期之外的提示语: {success_msg}"
    logging.info("测试通过：成功校验订单完成提示！")
