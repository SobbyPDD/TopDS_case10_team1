# file name: parser/smart_parser.py
import random
import time
import logging
from selenium.webdriver.common.by import By
from .classes import Review

logger = logging.getLogger(__name__)

def mode_reviews_smart(driver, filepath, limit=None, org_id=None):
    """Умный парсинг с прокруткой"""
    from .main import save_json
    
    time.sleep(2)
    
    data = []
    scroll_attempts = 0
    max_scrolls = 30
    
    while (limit is None or len(data) < limit) and scroll_attempts < max_scrolls:
        # Находим все видимые отзывы
        review_elems = driver.find_elements(
            By.XPATH, '//*[@class="business-review-view__info"]'
        )
        
        # Парсим каждый новый отзыв
        for i, review_elem in enumerate(review_elems[len(data):], start=len(data)):
            if limit and len(data) >= limit:
                break
                
            try:
                # Прокручиваем к отзыву
                driver.execute_script("arguments[0].scrollIntoView(true);", review_elem)
                time.sleep(0.1)
                
                new_review = Review(place_id=org_id)
                new_review.parse_base_information(review_elem=review_elem)
                
                if new_review.datetime:
                    review_data = {
                        'review_rating': new_review.review_rating,
                        'datetime': new_review.datetime,
                        'place_id': new_review.place_id,
                    }
                    
                    # Проверяем дубликаты
                    if not any(d['datetime'] == review_data['datetime'] for d in data):
                        data.append(review_data)
                        logger.debug(f"Собран отзыв {len(data)}" + (f"/{limit}" if limit else ""))
                        
            except Exception as e:
                logger.debug(f"Ошибка парсинга отзыва: {e}")
                continue
        
        # Если собрали достаточно - выходим
        if limit and len(data) >= limit:
            break
            
        # Умная прокрутка
        time.sleep(random.uniform(0.5, 1.5))
        
        # Разные способы прокрутки
        if scroll_attempts % 3 == 0:
            driver.execute_script("window.scrollBy(0, 700);")
        elif scroll_attempts % 3 == 1:
            # Прокрутка к последнему отзыву
            if review_elems:
                driver.execute_script("arguments[0].scrollIntoView(true);", review_elems[-1])
        else:
            # Рандомная прокрутка
            driver.execute_script(f"window.scrollBy(0, {random.randint(500, 900)});")
        
        scroll_attempts += 1
        
        # Если долго нет прогресса - выходим
        if scroll_attempts > 10 and len(data) == 0:
            logger.warning("Отзывы не загружаются")
            break
            
        if scroll_attempts % 5 == 0:
            logger.info(f"Прокруток: {scroll_attempts}, собрано отзывов: {len(data)}")
    
    # Сохраняем
    save_json(data, filepath)
    logger.info(f"Собрано {len(data)} отзывов для организации {org_id}")