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
    logging.info("步骤 1：登录成功")

    # 2. 浏览并添加商品
    inventory_page = InventoryPage(driver)
    inventory_page.add_backpack_to_cart()
    inventory_page.go_to_cart()
    logging.info("步骤 2：商品已添加至购物车")

    # 3. 购物车确认
    cart_page = CartPage(driver)
    cart_page.proceed_to_checkout()
    logging.info("步骤 3：进入结算页面")

    # 4. 填写信息并下单
    checkout_page = CheckoutPage(driver)
    checkout_page.fill_info_and_continue("Test", "User", "12345")
    checkout_page.finish_order()
    logging.info("步骤 4：订单提交完成")

    # 5. 断言验证
    success_msg = checkout_page.get_success_message()
    assert success_msg == "Thank you for your order!", f"预期之外的提示语: {success_msg}"
    logging.info("测试通过：成功校验订单完成提示！")