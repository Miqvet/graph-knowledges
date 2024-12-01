import requests
from rdflib import Graph, Namespace, RDF, URIRef, RDFS
import time

# Загружаем существующую онтологию
g = Graph()
g.parse("empty-graph.rdf")

# Определяем пространства имен
owl = Namespace("http://www.example.org/ontologies/videogames#")

# API ключ RAWG
API_KEY = "9b25260cec3c4e10b3a64c39cf04ef37"

# Функция для получения данных с API
def get_rawg_data(endpoint):
    base_url = f"https://api.rawg.io/api/{endpoint}"
    params = {
        "key": API_KEY,
        "page_size": 100  # Максимальный размер страницы
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()["results"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return []

# Получаем жанры
print("Получаем жанры...")
genres = get_rawg_data("genres")
time.sleep(1)  # Задержка между запросами
print(genres)
# Получаем платформы
print("Получаем платформы...")
platforms = get_rawg_data("platforms")
time.sleep(1)
print(platforms)

# Словарь для классификации платформ
# platform_categories = {
#     "mobile": ["Android", "iOS", "Windows Phone"],
#     "pc": ["PC", "macOS", "Linux"],
#     "console": ["PlayStation", "Xbox", "Nintendo", "Wii", "Sega"]
# }

# # Добавляем жанры в онтологию
# for genre in genres:
#     genre_slug = genre["slug"]
#     genre_uri = URIRef(owl + genre_slug)
#     g.add((genre_uri, RDF.type, owl.Genre))
#     print(f"Добавлен жанр: {genre_slug}")

# # Добавляем платформы в онтологию
# for platform in platforms:
#     platform_slug = platform["slug"]
#     platform_uri = URIRef(owl + platform_slug)
    
#     # Определяем тип платформы
#     platform_name = platform["name"]
    
#     if any(mobile in platform_name for mobile in platform_categories["mobile"]):
#         g.add((platform_uri, RDF.type, owl.MobilePlatform))
#         platform_type = "MobilePlatform"
#     elif any(pc in platform_name for pc in platform_categories["pc"]):
#         g.add((platform_uri, RDF.type, owl.PCPlatform))
#         platform_type = "PCPlatform"
#     else:
#         g.add((platform_uri, RDF.type, owl.Console))
#         platform_type = "Console"
    
#     print(f"Добавлена платформа: {platform_slug} (Тип: {platform_type})")

# # Сохраняем обновленную онтологию
# g.serialize(destination="updated-graph1.rdf", format="xml")
# print("Онтология успешно обновлена и сохранена!")