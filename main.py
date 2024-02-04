import sys
from io import BytesIO
from DeltaFinding import delta_finding
# Этот класс поможет нам сделать картинку из потока байт

import math

import requests
from PIL import Image


# Функция для определения расстояния по 2 точкам с долготой и широтой
def haversine(lat1, lon1, lat2, lon2):
    # Конвертируем градусы в радианы
    lon1, lat1, lon2, lat2 = map(math.radians, list(map(float, [lon1, lat1, lon2, lat2])))

    # Формула гаверсинуса
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Для нахождения расстояния домножим на радиус Земли равный 6371 километров
    km = 6371 * c
    return km


# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
# toponym_to_find = " ".join(sys.argv[1:])
toponym_to_find = ' '.join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    print(response.status_code)
    raise Exception
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coordinates = toponym["Point"]["pos"].split()

# Ищем ближайшею аптеку
search_api_server = "https://search-maps.yandex.ru/v1/"

address_ll = ','.join(toponym_coordinates)


search_params = {
    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print(response.status_code)
    raise Exception
    pass

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]
org_hours = organization['properties']["CompanyMetaData"]['Hours']['text']

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl~{1},pm2rdm".format(org_point, address_ll)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

if not response:
    print(response.status_code)
    raise Exception

print(f'Адрес: {org_address}')
print(f'Название: {org_name}')
print(f'Время работы: {org_hours}')
print(f'Расстояние: {round(haversine(*point, *toponym_coordinates), 2)} КМ')

Image.open(BytesIO(
    response.content)).show()
# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы
