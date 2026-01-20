# file name: batch_parser.py
import argparse
import time
import random
import json
import os
import logging
from typing import List
from datetime import datetime

from selenium.webdriver.common.by import By
from parser.selenium_helper import make_driver
from parser.classes import Review
from parser.main import save_json
from parser.log import configure_logging

logger = logging.getLogger(__name__)

def read_ids_from_file(filepath: str) -> List[int]:
    """Чтение ID организаций из файла"""
    ids = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        ids.append(int(line))
                    except ValueError:
                        logger.warning(f"Неверный формат ID: {line}")
        return ids
    except FileNotFoundError:
        logger.error(f"Файл не найден: {filepath}")
        return []

def parse_single_org_smart(driver, org_id, limit):
    """Парсинг одной организации (smart режим) прямо в память"""
    from parser.main import save_json
    
    # Открываем страницу
    url = f"https://yandex.ru/maps/org/yandeks/{org_id}/reviews/"
    driver.get(url)
    time.sleep(2)
    
    org_reviews = []
    scroll_attempts = 0
    max_scrolls = 30
    
    while (limit is None or len(org_reviews) < limit) and scroll_attempts < max_scrolls:
        # Находим все видимые отзывы
        review_elems = driver.find_elements(
            By.XPATH, '//*[@class="business-review-view__info"]'
        )
        
        # Парсим каждый новый отзыв
        for i, review_elem in enumerate(review_elems[len(org_reviews):], start=len(org_reviews)):
            if limit and len(org_reviews) >= limit:
                break
                
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", review_elem)
                time.sleep(0.1)
                
                new_review = Review(place_id=org_id)
                new_review.parse_base_information(review_elem=review_elem)
                
                if new_review.datetime:
                    review_data = {
                        'review_rating': new_review.review_rating,
                        'datetime': new_review.datetime,
                        'place_id': org_id,
                    }
                    
                    # Проверяем дубликаты
                    if not any(d['datetime'] == review_data['datetime'] for d in org_reviews):
                        org_reviews.append(review_data)
                        
            except Exception as e:
                logger.debug(f"Ошибка парсинга: {e}")
                continue
        
        if limit and len(org_reviews) >= limit:
            break
            
        # Прокрутка
        time.sleep(random.uniform(0.5, 1.5))
        driver.execute_script("window.scrollBy(0, 600);")
        scroll_attempts += 1
        
        if scroll_attempts > 10 and len(org_reviews) == 0:
            break
    
    return org_reviews

def parse_multiple_to_single_file(
    ids: List[int],
    output_file: str,
    limit_per_org: int = 50,
    debug: bool = False,
    min_delay: int = 2,
    max_delay: int = 2,
    headless: bool = True
):
    """
    Парсинг нескольких организаций в один файл БЕЗ временных файлов
    """
    if not ids:
        logger.error("Список ID организаций пуст")
        return
    
    # Создаем директорию если нужно
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Загружаем существующие данные
    all_reviews = []
    existing_place_ids = set()
    
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                all_reviews = existing_data
                for review in existing_data:
                    if 'place_id' in review:
                        existing_place_ids.add(review['place_id'])
                logger.info(f"Загружено {len(all_reviews)} существующих отзывов")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла: {e}")
    
    driver = make_driver(debug=not headless)
    
    try:
        for i, org_id in enumerate(ids, 1):
            logger.info(f"[{i}/{len(ids)}] Парсинг организации ID: {org_id}")
            
            # Если уже есть отзывы от этой организации, можно пропустить
            if org_id in existing_place_ids:
                logger.info(f"Организация {org_id} уже есть в файле, пропускаем")
                continue
            
            try:
                # Парсим организацию ПРЯМО В ПАМЯТЬ
                org_reviews = parse_single_org_smart(
                    driver=driver,
                    org_id=org_id,
                    limit=limit_per_org
                )
                
                # Добавляем к общему списку
                all_reviews.extend(org_reviews)
                logger.info(f"Добавлено {len(org_reviews)} отзывов от организации {org_id}")
                
                # Сразу сохраняем в файл
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_reviews, f, ensure_ascii=False, indent=2)
                logger.info(f"Промежуточное сохранение: всего {len(all_reviews)} отзывов")
                
            except Exception as e:
                logger.error(f"Ошибка при парсинге организации {org_id}: {str(e)}")
                continue
            
            # Случайная задержка между организациями
            if i < len(ids):
                delay = random.randint(min_delay, max_delay)
                logger.info(f"Задержка {delay} сек перед следующей организацией...")
                time.sleep(delay)
        
        logger.info(f"Парсинг завершен. Всего собрано {len(all_reviews)} отзывов")
        
    finally:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Пакетный парсинг нескольких организаций в один файл')
    
    # Источники ID
    parser.add_argument('--ids', type=int, nargs='+', help='Список ID организаций (через пробел)')
    parser.add_argument('--id-file', type=str, help='Файл со списком ID организаций (по одному на строке)')
    
    # Выходной файл
    parser.add_argument('--output', type=str, required=True, help='Путь к выходному файлу (все отзывы будут здесь)')
    
    # Параметры парсинга
    parser.add_argument('--limit', type=int, default=50,
                       help='Лимит отзывов на организацию (default: 50)')
    parser.add_argument('--min-delay', type=int, default=2,
                       help='Минимальная задержка между организациями в секундах (default: 2)')
    parser.add_argument('--max-delay', type=int, default=2,
                       help='Максимальная задержка между организациями в секундах (default: 2)')
    
    # Флаги
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    parser.add_argument('--no-headless', action='store_true', help='Запустить браузер в обычном режиме')
    
    args = parser.parse_args()
    
    # Настраиваем логирование
    configure_logging(debug=args.debug)
    
    # Получаем список ID
    ids = []
    
    if args.ids:
        ids.extend(args.ids)
        logger.info(f"Получено {len(args.ids)} ID из аргументов")
    
    if args.id_file:
        file_ids = read_ids_from_file(args.id_file)
        ids.extend(file_ids)
        logger.info(f"Получено {len(file_ids)} ID из файла {args.id_file}")
    
    if not ids:
        logger.error("Не указаны ID организаций. Используйте --ids или --id-file")
        return
    
    # Убираем дубликаты
    unique_ids = list(dict.fromkeys(ids))
    if len(ids) != len(unique_ids):
        logger.info(f"Удалено {len(ids) - len(unique_ids)} дубликатов ID")
    
    logger.info(f"Всего организаций для парсинга: {len(unique_ids)}")
    logger.info(f"Лимит отзывов на организацию: {args.limit}")
    logger.info(f"Задержка между организациями: {args.min_delay}-{args.max_delay} сек")
    logger.info(f"Выходной файл: {args.output}")
    
    # Запускаем парсинг
    parse_multiple_to_single_file(
        ids=unique_ids,
        output_file=args.output,
        limit_per_org=args.limit,
        debug=args.debug,
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        headless=not args.no_headless
    )

if __name__ == '__main__':
    main()