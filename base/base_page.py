from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import get_timeout


class BasePage:
    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout or get_timeout())

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.find(locator).click()

    def input_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text

    def current_url(self):
        return self.driver.current_url
