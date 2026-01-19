ymaps.ready(initMap);

let map, objectManager;
let minSize = 5, maxSize = 30;
let circleCache = {};

async function initMap() {
    // Создаем карту
    map = new ymaps.Map('map', {
        center: [55.76, 37.64],
        zoom: 10
    });
    
    // Создаем ObjectManager с кластеризацией
    objectManager = new ymaps.ObjectManager({
        clusterize: true,
        gridSize: 64,
        clusterDisableClickZoom: true
    });
    
    // Настройка кластеров
    objectManager.clusters.options.set({
        preset: 'islands#invertedBlueClusterIcons',
        clusterNumbersSize: 24
    });

    // Настройки объектов
    objectManager.objects.options.set({
        iconLayout: 'default#image',
        iconImageSize: [15, 15],
        iconImageHref: getCircleImageUrl('#33cc33', 15),
        iconImageOffset: [-7.5, -7.5],
        hasBalloon: true,
        hasHint: true,
        balloonContentHeader: '{properties.name}',
        balloonContentBody: '{properties.balloonContent}', // Используем кастомное свойство
        balloonCloseButton: true
    });
    
    // Обработчик клика на объекты
    objectManager.objects.events.add('click', function (e) {
        const objectId = e.get('objectId');
        const object = objectManager.objects.getById(objectId);
        
        // Открываем балун для объекта
        objectManager.objects.balloon.open(objectId);
    });
    
    map.geoObjects.add(objectManager);
    
    // Загружаем и отображаем компании
    await loadAndDisplayCompanies();
    
    // Сразу обновляем круги после загрузки
    updateCircleSizes();
    
    // Настройка контролов
    document.getElementById('updateSizes').addEventListener('click', updateCircleSizes);
    document.getElementById('minSize').addEventListener('input', (e) => {
        minSize = parseInt(e.target.value);
        updateCircleSizes();
    });
    document.getElementById('maxSize').addEventListener('input', (e) => {
        maxSize = parseInt(e.target.value);
        updateCircleSizes();
    });
}

async function loadAndDisplayCompanies() {
    const features = [];
    
    // Обрабатываем пачками по batchSize штук
    const batchSize = 50;
    
    for (let i = 0; i < companyData.length; i += batchSize) {
        const batch = companyData.slice(i, i + batchSize);
        const promises = batch.map(company => 
            getCompanyCoordinates(company.id, company) 
                .then(coords => ({
                    ...company,
                    coords
                }))
                .catch(() => null)
        );
        
        const results = await Promise.all(promises);
        
        // Добавляем успешные результаты
        results.filter(Boolean).forEach((company, index) => {
            if (company.coords) {
                const value = company.value;
                const size = calculateSize(value, minSize, maxSize);
                const color = getColorByValue(value);
                
                // Формируем HTML для балуна
                const balloonHTML = `
                    <div style="padding: 10px; font-family: Arial, sans-serif;">
                        <h3 style="margin: 0 0 10px 0;">${company.name || 'Компания'}</h3>
                        <p style="margin: 5px 0;">Значение: <strong>${company.value}</strong></p>
                        <p style="margin: 5px 0;">ID: ${company.id}</p>
                        <a href="https://yandex.ru/maps/org/${company.id}" 
                           target="_blank" 
                           style="display: inline-block; margin-top: 10px; padding: 5px 10px; background: #f33; color: white; text-decoration: none; border-radius: 3px;">
                            Открыть в Яндекс.Картах
                        </a>
                    </div>
                `;
                
                features.push({
                    type: 'Feature',
                    id: i + index,
                    geometry: {
                        type: 'Point',
                        coordinates: [company.coords[0], company.coords[1]]
                    },
                    properties: {
                        name: company.name || `Компания ${company.id}`,
                        yandexId: company.id,
                        value: value,
                        iconColor: color,
                        iconSize: size,
                        balloonContent: balloonHTML
                    }
                });
            }
        });
        
        // Обновляем карту постепенно
        if (features.length > 0) {
            objectManager.add({
                type: 'FeatureCollection',
                features: features.slice(-batchSize)
            });
            
            // Автоматически подбираем масштаб
            if (i === 0) {
                map.setBounds(objectManager.getBounds(), {
                    checkZoomRange: true
                });
            }
        }
    }
    
    console.log(`Загружено ${features.length} компаний из ${companyData.length}`);
}

async function getCompanyCoordinates(yandexId, companyObj) {
    if (companyObj && companyObj.coords) {
        const cacheKey = `yandex_coords_${yandexId}`;
        localStorage.setItem(cacheKey, JSON.stringify(companyObj.coords));
        return companyObj.coords;
    }

    const cacheKey = `yandex_coords_${yandexId}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
        console.log(`Используем кеш для ID: ${yandexId}`);
        return JSON.parse(cached);
    }

    console.warn(`Нет координат для ID: ${yandexId}. Добавьте вручную в companyData.`);
    return null;
}

function updateCircleSizes() {
    console.log('Обновление размеров и цветов...');
    
    // Получаем все объекты
    const allObjects = objectManager.objects.getAll();
    
    // Обновляем КАЖДЫЙ объект
    for (let id in allObjects) {
        if (allObjects.hasOwnProperty(id)) {
            const obj = allObjects[id];
            const value = obj.properties.value || 0;
            const size = calculateSize(value, minSize, maxSize);
            const color = getColorByValue(value);
            
            // Обновляем иконку
            objectManager.objects.setObjectOptions(id, {
                iconImageSize: [size, size],
                iconImageHref: getCircleImageUrl(color, size),
                iconImageOffset: [-size/2, -size/2]
            });
        }
    }
    
    console.log(`Обновлено ${Object.keys(allObjects).length} объектов`);
}

function getCircleImageUrl(color, size) {
    // Рисуем картинку кружочка :)
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
            <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="${color}"/>
            <circle cx="${size/2}" cy="${size/2}" r="${size/3}" fill="white"/>
            <circle cx="${size/2}" cy="${size/2}" r="${size/4}" fill="${color}"/>
        </svg>
    `;
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
}

function calculateSize(value, min, max) {
    const allValues = companyData.map(c => c.value);
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    
    // Защита от деления на ноль
    if (maxValue === minValue) return (min + max) / 2;
    
    const normalized = (value - minValue) / (maxValue - minValue);
    const size = min + normalized * (max - min);
    
    return size;
}

function getColorByValue(value) {
    if (value > 60) return '#ff3333';
    if (value > 40) return '#ff9900';
    if (value > 25) return '#ffcc00';
    return '#33cc33';
}