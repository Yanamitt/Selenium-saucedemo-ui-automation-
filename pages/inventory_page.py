from selenium.webdriver.common.by import By
from base.base_page import BasePage

class InventoryPage(BasePage):
    # Locators
    ADD_BACKPACK_BTN = (By.ID, "add-to-cart-sauce-labs-backpack")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")
    REMOVE_BACKPACK_BTN = (By.ID, "remove-sauce-labs-backpack")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge") # 购物车右上角的数字图标
    
    def add_backpack_to_cart(self):
        self.click(self.ADD_BACKPACK_BTN)

    def go_to_cart(self):
        self.click(self.CART_ICON)
        
    def remove_backpack(self):
        self.click(self.REMOVE_BACKPACK_BTN)

    def get_cart_count(self):
        """获取购物车显示的商品数量，如果为空则捕获异常返回 0"""
        try:
            return self.get_text(self.CART_BADGE)
        except:
            return "0"    