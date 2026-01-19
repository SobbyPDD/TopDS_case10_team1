import logging
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger: logging.Logger = logging.getLogger(__name__)


def make_driver(debug=False):
    options = Options()
    options.page_load_strategy = 'eager'
    # Оптимизация для ускорения
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)

    # Отключаем изображения для ускорения
    options.set_preference('permissions.default.image', 2)

    if not debug:
        options.add_argument("--headless")

    return webdriver.Firefox(options=options)


def get_element_by_xpath(
        driver: Firefox,
        xpath: str,
) -> WebElement:
    elem = driver.find_element(by=By.XPATH, value=xpath)
    return elem


def wait_element_by_xpath(
        driver: Firefox,
        xpath: str,
        timeout: int = 10
) -> WebElement:
    logger.debug(f'wait_element_by_xpath start {xpath=}')

    for attempt_number in range(1, 4):  # Уменьшил количество попыток
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            logger.debug(f"Element found {attempt_number=} {elem.id=}")
            return elem
        except (StaleElementReferenceException, TimeoutException) as e:
            logger.debug(f"Retry {attempt_number=} for {xpath}: {e}")
            time.sleep(1)

    raise Exception(f"Element not found after retries: {xpath}")