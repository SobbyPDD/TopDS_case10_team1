import random
import json
import math

def generate_random_id():
    """Генерация случайного 10-12 значного числа в виде строки"""
    length = random.randint(10, 12)
    first_digit = random.randint(1, 9)
    other_digits = ''.join(str(random.randint(0, 9)) for _ in range(length - 1))
    return str(first_digit) + other_digits

def normal_distribution_coords(lat_center=59.5, lon_center=30.5, lat_std=0.2, lon_std=0.2):
    """
    Генерация координат с нормальным распределением
    
    Args:
        lat_center: центр распределения по широте (медиана)
        lon_center: центр распределения по долготе (медиана)
        lat_std: стандартное отклонение по широте
        lon_std: стандартное отклонение по долготе
    """
    def truncate(value, min_val, max_val):
        """Ограничиваем значение заданными границами"""
        return max(min_val, min(max_val, value))
    
    # Генерируем координаты с нормальным распределением
    lat = random.gauss(lat_center, lat_std)
    lon = random.gauss(lon_center, lon_std)
    
    # Обрезаем значения до заданных диапазонов
    lat = truncate(lat, 59.0, 60.0)
    lon = truncate(lon, 30.0, 31.0)
    
    return [round(lat, 6), round(lon, 6)]

def generate_random_coords():
    """Генерация случайных координат с нормальным распределением"""
    return normal_distribution_coords(lat_center=59.5, lon_center=30.5, lat_std=0.18, lon_std=0.18)

def generate_average_rating():
    """
    Генерация случайного среднего рейтинга от 1 до 5
    
    Можно сделать разное распределение:
    1. Реалистичное (большинство оценок 3-5)
    2. Равномерное (1-5 равновероятно)
    3. Смещенное (для тестирования)
    """
    # Вариант 1: Реалистичное распределение (более вероятны высокие оценки)
    # Используем бета-распределение с пиком около 4.0-4.5
    rating = random.betavariate(5, 2) * 4 + 1  # От 1 до 5
    
    # Вариант 2: Нормальное распределение с центром в 4.0
    # rating = random.gauss(4.0, 0.8)
    # rating = max(1.0, min(5.0, rating))
    
    # Вариант 3: Просто равномерное распределение
    # rating = random.uniform(1.0, 5.0)
    
    return round(rating, 2)

def generate_reviews_num():
    """
    Генерация случайного количества отзывов от 10 до 10000
    
    Обычно распределение по отзывам смещено - мало объектов с большим количеством отзывов
    """
    # Вариант 1: Экспоненциальное распределение (реалистичное)
    # Большинство объектов имеют мало отзывов, некоторые - очень много
    lam = 0.0005  # Параметр экспоненциального распределения
    reviews = random.expovariate(lam)
    reviews = min(10000, max(10, int(reviews)))
    
    # Вариант 2: Логарифмическое распределение
    # reviews = int(math.exp(random.uniform(math.log(10), math.log(10000))))
    
    # Вариант 3: Равномерное распределение в логарифмической шкале
    # log_reviews = random.uniform(math.log10(10), math.log10(10000))
    # reviews = int(10 ** log_reviews)
    
    # Вариант 4: Просто равномерное распределение
    # reviews = random.randint(10, 10000)
    
    return reviews

def generate_random_coords_with_clusters(num_clusters=3):
    """
    Альтернативный вариант: несколько кластеров (скоплений) точек
    """
    cluster_centers = []
    for i in range(num_clusters):
        lat_center = 59.3 + random.random() * 0.7
        lon_center = 30.3 + random.random() * 0.7
        cluster_centers.append((lat_center, lon_center))
    
    cluster_idx = random.choices(
        range(num_clusters), 
        weights=[0.4] + [0.6/(num_clusters-1)] * (num_clusters-1)
    )[0]
    
    lat_center, lon_center = cluster_centers[cluster_idx]
    return normal_distribution_coords(lat_center, lon_center, lat_std=0.1, lon_std=0.1)

def generate_data(use_clusters=False):
    """Генерация данных для 500 записей"""
    company_data = []
    
    for i in range(500):
        if use_clusters:
            coords = generate_random_coords_with_clusters(num_clusters=3)
        else:
            coords = generate_random_coords()
        
        record = {
            'id': generate_random_id(),
            'averageRating': generate_average_rating(),
            'reviewsNum': generate_reviews_num(),
            'name': str(i),
            'coords': coords
        }
        company_data.append(record)
    
    return company_data

def analyze_distribution(data):
    """Анализ распределения сгенерированных данных"""
    # Координаты
    lats = [point['coords'][0] for point in data]
    lons = [point['coords'][1] for point in data]
    
    # Рейтинги
    ratings = [point['averageRating'] for point in data]
    
    # Отзывы
    reviews = [point['reviewsNum'] for point in data]
    
    print("\n" + "="*60)
    print("АНАЛИЗ РАСПРЕДЕЛЕНИЯ ДАННЫХ")
    print("="*60)
    
    print("\n📊 КООРДИНАТЫ:")
    print(f"   Широта: мин={min(lats):.4f}, макс={max(lats):.4f}, среднее={sum(lats)/len(lats):.4f}")
    print(f"   Долгота: мин={min(lons):.4f}, макс={max(lons):.4f}, среднее={sum(lons)/len(lons):.4f}")
    
    # Гистограмма по квадрантам
    quadrants = {'северо-запад': 0, 'северо-восток': 0, 'юго-запад': 0, 'юго-восток': 0}
    for lat, lon in zip(lats, lons):
        if lat >= 59.5 and lon >= 30.5:
            quadrants['северо-восток'] += 1
        elif lat >= 59.5 and lon < 30.5:
            quadrants['северо-запад'] += 1
        elif lat < 59.5 and lon >= 30.5:
            quadrants['юго-восток'] += 1
        else:
            quadrants['юго-запад'] += 1
    
    print("\n   Распределение по квадрантам (относительно центра 59.5, 30.5):")
    for quadrant, count in quadrants.items():
        percentage = (count / len(data)) * 100
        print(f"     {quadrant}: {count} точек ({percentage:.1f}%)")
    
    print("\n⭐ РЕЙТИНГИ (averageRating):")
    print(f"   Мин: {min(ratings):.2f}, Макс: {max(ratings):.2f}, Среднее: {sum(ratings)/len(ratings):.2f}")
    
    # Распределение по диапазонам рейтингов
    rating_ranges = {'1-2': 0, '2-3': 0, '3-4': 0, '4-5': 0}
    for rating in ratings:
        if rating < 2:
            rating_ranges['1-2'] += 1
        elif rating < 3:
            rating_ranges['2-3'] += 1
        elif rating < 4:
            rating_ranges['3-4'] += 1
        else:
            rating_ranges['4-5'] += 1
    
    print("\n   Распределение по диапазонам:")
    for range_name, count in rating_ranges.items():
        percentage = (count / len(data)) * 100
        print(f"     {range_name}: {count} ({percentage:.1f}%)")
    
    print("\n💬 ОТЗЫВЫ (reviewsNum):")
    print(f"   Мин: {min(reviews):,}, Макс: {max(reviews):,}, Среднее: {sum(reviews)/len(reviews):,.0f}")
    print(f"   Медиана: {sorted(reviews)[len(reviews)//2]:,}")
    
    # Распределение по диапазонам отзывов
    review_ranges = {
        '10-100': 0,
        '100-500': 0,
        '500-1000': 0,
        '1000-5000': 0,
        '5000-10000': 0
    }
    
    for review in reviews:
        if review < 100:
            review_ranges['10-100'] += 1
        elif review < 500:
            review_ranges['100-500'] += 1
        elif review < 1000:
            review_ranges['500-1000'] += 1
        elif review < 5000:
            review_ranges['1000-5000'] += 1
        else:
            review_ranges['5000-10000'] += 1
    
    print("\n   Распределение по диапазонам:")
    for range_name, count in review_ranges.items():
        percentage = (count / len(data)) * 100
        print(f"     {range_name}: {count} ({percentage:.1f}%)")
    
    print("\n📈 КОРРЕЛЯЦИЯ РЕЙТИНГА И КОЛИЧЕСТВА ОТЗЫВОВ:")
    # Простая проверка на корреляцию
    high_rating_many_reviews = sum(1 for p in data if p['averageRating'] > 4.0 and p['reviewsNum'] > 1000)
    low_rating_few_reviews = sum(1 for p in data if p['averageRating'] < 2.5 and p['reviewsNum'] < 100)
    
    print(f"   Высокий рейтинг (>4.0) и много отзывов (>1000): {high_rating_many_reviews} объектов")
    print(f"   Низкий рейтинг (<2.5) и мало отзывов (<100): {low_rating_few_reviews} объектов")

def save_to_file(data, filename='companyData.js'):
    """Сохранение данных в файл в указанном формате"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("const companyData = [\n")
        
        for i, record in enumerate(data):
            f.write("    { \n")
            f.write(f"        id: '{record['id']}', \n")
            f.write(f"        averageRating: {record['averageRating']}, \n")
            f.write(f"        reviewsNum: {record['reviewsNum']}, \n")
            f.write(f"        name: '{record['name']}',\n")
            f.write(f"        coords: [{record['coords'][0]}, {record['coords'][1]}] \n")
            f.write("    }")
            
            if i < len(data) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        
        f.write("];\n")
    
    print(f"\n✅ Данные успешно сохранены в файл: {filename}")
    print(f"📊 Сгенерировано записей: {len(data)}")

def main():
    """Основная функция"""
    print("="*60)
    print("ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ ДЛЯ КОМПАНИЙ")
    print("="*60)
    print("\nПараметры генерации:")
    print("  • 500 записей")
    print("  • ID: 10-12 значные числа")
    print("  • averageRating: 1.0-5.0")
    print("  • reviewsNum: 10-10000")
    print("  • Координаты: центрированы вокруг (59.5, 30.5)")
    print("="*60)
    
    # Настройка метода генерации
    use_clusters = False  # True для нескольких кластеров
    
    print("\n🎲 Генерация данных...")
    data = generate_data(use_clusters=use_clusters)
    
    # Анализ распределения
    analyze_distribution(data)
    
    # Сохранение в файл
    save_to_file(data)
    
    # Примеры данных
    print("\n" + "="*60)
    print("ПРИМЕРЫ СГЕНЕРИРОВАННЫХ ДАННЫХ")
    print("="*60)
    
    # Покажем первые 3 записи
    for i in range(3):
        print(f"\nЗапись #{i}:")
        print(f"  id: {data[i]['id']}")
        print(f"  averageRating: {data[i]['averageRating']}")
        print(f"  reviewsNum: {data[i]['reviewsNum']:,}")
        print(f"  name: {data[i]['name']}")
        print(f"  coords: {data[i]['coords']}")
    
    # Покажем некоторые экстремальные значения
    print("\n" + "-"*40)
    print("ЭКСТРЕМАЛЬНЫЕ ЗНАЧЕНИЯ:")
    
    max_rating = max(data, key=lambda x: x['averageRating'])
    min_rating = min(data, key=lambda x: x['averageRating'])
    max_reviews = max(data, key=lambda x: x['reviewsNum'])
    min_reviews = min(data, key=lambda x: x['reviewsNum'])
    
    print(f"\n📈 Самый высокий рейтинг: {max_rating['averageRating']} (id: {max_rating['id']})")
    print(f"📉 Самый низкий рейтинг: {min_rating['averageRating']} (id: {min_rating['id']})")
    print(f"💬 Больше всего отзывов: {max_reviews['reviewsNum']:,} (id: {max_reviews['id']})")
    print(f"🔇 Меньше всего отзывов: {min_reviews['reviewsNum']} (id: {min_reviews['id']})")

if __name__ == "__main__":
    main()