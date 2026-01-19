
import argparse
import logging
from selenium import webdriver
from parser.log import configure_logging
from parser.main import get_organization_reviews


def main():
    parser = argparse.ArgumentParser(description='Парсер отзывов Яндекс Карт')
    parser.add_argument('--org_id', type=int, required=True, help='ID организации')
    parser.add_argument('--limit', type=int, default=None, help='Лимит отзывов')
    parser.add_argument('--mode', type=str, default='reviews', choices=['reviews', 'experimental'], help='Режим работы')
    parser.add_argument('--debug', action='store_true', help='Включить отладочный режим')
    parser.add_argument('--headless', action='store_true', help='Запуск браузера в фоновом режиме')
    parser.add_argument('--output', type=str, default=None, help='Путь к выходному файлу. Если не указан, используется папка json/reviews.json')

    args = parser.parse_args()

    # Настройка логирования
    configure_logging(debug=args.debug)

    # Создание драйвера
    from parser.selenium_helper import make_driver
    driver = make_driver(debug=not args.headless)

    try:
        get_organization_reviews(
            driver=driver,
            mode=args.mode,
            org_id=args.org_id,
            limit=args.limit,
            output_path=args.output
        )
    except Exception as e:
        logging.error(f"Ошибка при выполнении парсинга: {e}")
        raise
    finally:
        driver.quit()


if __name__ == '__main__':
    main()