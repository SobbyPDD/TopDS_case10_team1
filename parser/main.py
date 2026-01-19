
import datetime as dt
import json
import logging
import os
import re
import time

from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from parser import selenium_helper as sh
from parser.classes import Review

logger: logging.Logger = logging.getLogger(__name__)


def save_json(data, filepath):
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
    logger.info(f'Saved {filepath}')


def mode_script_content(driver: Firefox, filepath):
    script_element = driver.find_element(by='xpath', value='//script[@class="state-view"]')
    script_content = script_element.get_attribute("innerHTML")
    save_json(json.loads(script_content), filepath)


def mode_reviews(driver: Firefox, filepath, limit: int = None):
    # Ждем загрузки страницы
    time.sleep(3)

    total_reviews: WebElement = sh.wait_element_by_xpath(
        driver=driver,
        xpath='//*[@class="card-section-header__title _wide"]',
    )

    total_reviews_count: int = int(re.sub(pattern=r'\D', repl='', string=total_reviews.text))

    if limit is not None and limit < total_reviews_count:
        reviews_to_collect = limit
        logger.info(f"Лимит установлен. Будет собрано {reviews_to_collect} из {total_reviews_count} отзывов.")
    else:
        reviews_to_collect = total_reviews_count
        logger.info(f"Лимит не установлен. Будет собрано все {total_reviews_count} отзывов.")

    data = []
    for i in range(1, reviews_to_collect + 1):
        try:
            review_elem = sh.wait_element_by_xpath(
                xpath=f'''(//*[@class="business-review-view__info"])[{i}]''',
                driver=driver
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", review_elem)

            # Добавляем небольшую задержку для стабилизации
            time.sleep(0.1)

            new_review = Review()
            new_review.parse_base_information(review_elem=review_elem)

            # Формируем только необходимые поля
            review_data = {
                # 'author': new_review.author,
                'selenium_id': new_review.selenium_id,
                'review_text': new_review.review_text,
                'review_rating': new_review.review_rating,
                'datetime': new_review.datetime,
            }

            data.append(review_data)
            logger.debug(f"Собран отзыв {i}/{reviews_to_collect}")

        except Exception as e:
            logger.error(f"Ошибка при парсинге отзыва {i}: {e}")
            continue

    # Проверяем, существует ли файл
    if os.path.exists(filepath):
        logger.info(f"Файл {filepath} уже существует. Загружаем существующие данные...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                # Объединяем данные, избегая дубликатов по Selenium ID
                existing_ids = {item.get('selenium_id') for item in existing_data if 'selenium_id' in item}
                new_data = []
                for item in data:
                    item_id = item.get('selenium_id')
                    if item_id not in existing_ids:
                        new_data.append(item)

                if new_data:
                    combined_data = existing_data + new_data
                    logger.info(f"Добавлено {len(new_data)} новых отзывов к существующим {len(existing_data)}")
                    data = combined_data
                else:
                    logger.info("Нет новых отзывов для добавления")
                    data = existing_data
        except Exception as e:
            logger.error(f"Ошибка при чтении существующего файла: {e}. Создаем новый.")

    save_json(data, filepath)


# Режимы работы
MODE_DICT = {
    'reviews': mode_reviews,
    'experimental': mode_script_content,
}


def get_organization_reviews(driver: Firefox, mode: str, implicitly_wait: int = 0,
                             org_id: int = 1124715036, limit: int = None, output_path: str = None):
    organization_url = f"https://yandex.ru/maps/org/yandeks/{org_id}/reviews/"
    logger.info(f'Start {organization_url=} {implicitly_wait=}')
    driver.implicitly_wait(implicitly_wait)

    # Определяем путь к файлу
    if output_path:
        filepath = output_path
        logger.info(f"Используем указанный путь: {filepath}")
    else:
        # Если файл не указан, используем папку json и файл reviews.json
        json_dir = os.path.join(os.getcwd(), 'json')
        filepath = os.path.join(json_dir, 'reviews.json')
        logger.info(f"Путь не указан. Используем путь по умолчанию: {filepath}")

    driver.get(organization_url)
    MODE_DICT[mode](driver=driver, filepath=filepath, limit=limit)


if __name__ == '__main__':
    pass