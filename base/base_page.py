from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import get_timeout


class BasePage:
    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout or get_timeout())

    def wait_for_presence(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_visibility(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_for_invisibility(self, locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_all_visible(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def wait_for_url_contains(self, fragment):
        return self.wait.until(EC.url_contains(fragment))

    def find(self, locator):
        return self.wait_for_visibility(locator)

    def click(self, locator):
        self.wait_for_clickable(locator).click()

    def input_text(self, locator, text):
        element = self.wait_for_visibility(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.wait_for_visibility(locator).text

    def current_url(self):
        return self.driver.current_url
