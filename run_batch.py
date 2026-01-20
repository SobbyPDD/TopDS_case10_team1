# file name: batch_parser.py
import argparse
import os
import time
import logging
from typing import List

from selenium.webdriver import Firefox

from parser.selenium_helper import make_driver
from parser.main import get_organization_reviews
from parser.log import configure_logging

logger = logging.getLogger(__name__)


def read_ids_from_file(filepath: str) -> List[int]:
    """Чтение ID организаций из файла"""
    ids = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    try:
                        ids.append(int(line))
                    except ValueError:
                        logger.warning(f"Неверный формат ID: {line}")
        return ids
    except FileNotFoundError:
        logger.error(f"Файл не найден: {filepath}")
        return []


def parse_multiple_organizations(
    ids: List[int],
    mode: str = 'reviews',
    limit: int = None,
    output_dir: str = None,
    debug: bool = False,
    delay_between_requests: int = 2,
    implicitly_wait: int = 0
):
    """
    Парсинг нескольких организаций последовательно
    
    Args:
        ids: Список ID организаций
        mode: Режим парсинга ('reviews' или 'experimental')
        limit: Лимит отзывов для каждой организации
        output_dir: Директория для сохранения результатов
        debug: Режим отладки
        delay_between_requests: Задержка между запросами (в секундах)
        implicitly_wait: Ожидание неявных элементов
    """
    if not ids:
        logger.error("Список ID организаций пуст")
        return

    # Создаем драйвер
    driver = make_driver(debug=debug)
    
    try:
        for i, org_id in enumerate(ids, 1):
            logger.info(f"[{i}/{len(ids)}] Парсинг организации с ID: {org_id}")
            
            # Определяем путь для сохранения
            if output_dir:
                # Создаем директорию, если она не существует
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, f"reviews_{org_id}.json")
            else:
                # Используем стандартную директорию
                filepath = os.path.join(os.getcwd(), 'json', f"reviews_{org_id}.json")
            
            try:
                # Парсим организацию
                get_organization_reviews(
                    driver=driver,
                    mode=mode,
                    implicitly_wait=implicitly_wait,
                    org_id=org_id,
                    limit=limit,
                    output_path=filepath
                )
                
                logger.info(f"Успешно обработана организация {org_id}")
                
            except Exception as e:
                logger.error(f"Ошибка при парсинге организации {org_id}: {str(e)}")
                continue
            
            # Задержка между запросами (если не последняя организация)
            if i < len(ids) and delay_between_requests > 0:
                logger.info(f"Ожидание {delay_between_requests} секунд перед следующим запросом...")
                time.sleep(delay_between_requests)
    
    finally:
        # Закрываем драйвер
        driver.quit()
        logger.info("Парсинг завершен")


def main():
    parser = argparse.ArgumentParser(description='Парсинг нескольких организаций Яндекс.Карт')
    
    # Основные аргументы
    parser.add_argument('--ids', type=int, nargs='+', help='Список ID организаций (через пробел)')
    parser.add_argument('--id-file', type=str, help='Файл со списком ID организаций (по одному на строке)')
    parser.add_argument('--mode', type=str, default='reviews', 
                       choices=['reviews', 'experimental'],
                       help='Режим парсинга (default: reviews)')
    parser.add_argument('--limit', type=int, help='Лимит отзывов для каждой организации')
    parser.add_argument('--output-dir', type=str, help='Директория для сохранения результатов')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    parser.add_argument('--delay', type=int, default=2, 
                       help='Задержка между запросами в секундах (default: 2)')
    parser.add_argument('--wait', type=int, default=0,
                       help='Ожидание неявных элементов (default: 0)')
    
    args = parser.parse_args()
    
    # Настраиваем логирование
    configure_logging(debug=args.debug)
    
    # Получаем список ID
    ids = []
    
    if args.ids:
        ids.extend(args.ids)
    
    if args.id_file:
        file_ids = read_ids_from_file(args.id_file)
        ids.extend(file_ids)
    
    if not ids:
        logger.error("Не указаны ID организаций. Используйте --ids или --id-file")
        return
    
    # Убираем дубликаты
    ids = list(dict.fromkeys(ids))
    
    logger.info(f"Найдено {len(ids)} уникальных ID организаций")
    logger.info(f"Режим работы: {args.mode}")
    logger.info(f"Лимит отзывов: {args.limit if args.limit else 'нет'}")
    logger.info(f"Задержка между запросами: {args.delay} сек")
    
    # Запускаем парсинг
    parse_multiple_organizations(
        ids=ids,
        mode=args.mode,
        limit=args.limit,
        output_dir=args.output_dir,
        debug=args.debug,
        delay_between_requests=args.delay,
        implicitly_wait=args.wait
    )


if __name__ == '__main__':
    main()