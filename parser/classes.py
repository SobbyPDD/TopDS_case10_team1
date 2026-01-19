from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import logging

logger = logging.getLogger(__name__)


def try_get_child_elem_by_xpath(
        parent_element: WebElement, value: str
) -> WebElement or None:
    found_elem = parent_element.find_elements(
        by=By.XPATH, value=value
    )
    return found_elem[0] if found_elem else None


def try_found_elem_if_exist_return_attr(
        parent_element: WebElement or None,
        attribute: str,
) -> str or None:
    if parent_element:  # is WebElement
        return parent_element.get_attribute(attribute)


def try_found_elem_if_exist_return_text(
        parent_element: WebElement or None
) -> str or None:
    if parent_element:
        return parent_element.text


class Review:
    """class for reviews"""

    def __repr__(self):
        return repr(self.__dict__)

    def __init__(self, **kwargs):
        # Оставляем только необходимые поля
        # self.author = None
        # self.review_text = None
        self.review_rating = None
        self.datetime = None
        # self.selenium_id = None
        self.place_id = None  # Добавляем поле place_id

        for key, value in kwargs.items():
            setattr(self, key, value)

    def parse_base_information(
            self, review_elem: WebElement
    ):
        # self.selenium_id = review_elem.id
        # Получаем имя автора
        # try:
        #     author_elem = review_elem.find_element(
        #         By.XPATH, './/*[@itemtype="http://schema.org/Person"]//meta[@itemprop="name"]'
        #     )
        #     self.author = author_elem.get_attribute("content")
        # except:
        #     self.author = None

        # Получаем дату
        try:
            date_elem = review_elem.find_element(
                By.XPATH, './/*[@class="business-review-view__date"]//meta[@itemprop="datePublished"]'
            )
            self.datetime = date_elem.get_attribute("content")
        except:
            self.datetime = None

        # Получаем рейтинг
        try:
            rating_elem = review_elem.find_element(
                By.XPATH, './/*[@itemtype="http://schema.org/Rating"]//meta[@itemprop="ratingValue"]'
            )
            self.review_rating = rating_elem.get_attribute("content")
        except:
            self.review_rating = None

        # Получаем текст отзыва
        # try:
        #     text_elem = review_elem.find_element(
        #         By.XPATH, './/*[@class="business-review-view__body"]'
        #     )
        #     self.review_text = text_elem.text.strip()
        # except:
        #     self.review_text = None


if __name__ == '__main__':
    pass