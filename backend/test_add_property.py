import requests
import json

# URL для добавления объекта
url = "http://localhost:8000/admin/add"

# Данные тестового объекта
data = {
    'title': 'Тестовая новостройка в Пратамнаке',
    'condo_name': 'Zenith Tower',
    'district': 'Пратамнак',
    'location': 'Паттайя',
    'property_type': 'apartment',
    'status': 'available',
    'price': '25000',
    'price_period': 'month',
    'bedrooms': '2',
    'bathrooms': '2',
    'area': '75',
    'floor': '15',
    'furnished': 'Полностью',
    'published_at': '2025-06-27',
    'lat': '12.9236',
    'lng': '100.8824',
    'description': 'Современная новостройка с видом на море. Полностью меблированная квартира с 2 спальнями.',
    'is_new_building': 'true'
}

# Отправляем POST запрос
try:
    response = requests.post(url, data=data)
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.text[:500]}...")  # Первые 500 символов ответа
    
    if response.status_code == 200:
        print("✅ Объект успешно добавлен!")
        print("Теперь проверьте каталог новостроек: http://localhost:8000/ru/properties/new-builds")
    else:
        print("❌ Ошибка при добавлении объекта")
        
except Exception as e:
    print(f"❌ Ошибка: {e}") 