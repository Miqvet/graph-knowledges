import requests
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

API_KEY = "9b25260cec3c4e10b3a64c39cf04ef37"

def get_genres():
    url = f"https://api.rawg.io/api/genres?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        genres = response.json()['results']
        return [genre['name'] for genre in genres]
    return []

def get_platforms():
    url = f"https://api.rawg.io/api/platforms?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        platforms = response.json()['results']
        return [platform['name'] for platform in platforms]
    return []

def get_games(count=100):
    games = []
    page_size = 40  # Максимальный размер страницы API
    pages_needed = (count + page_size - 1) // page_size
    
    for page in range(1, pages_needed + 1):
        url = f"https://api.rawg.io/api/games?key={API_KEY}&page={page}&page_size={page_size}"
        response = requests.get(url)
        if response.status_code == 200:
            games.extend(response.json()['results'])
            if len(games) >= count:
                return games[:count]
    return games[:count]

# Получаем и выводим списки
genres = get_genres()
platforms = get_platforms()
# Создаем граф и загружаем существующую онтологию
g = Graph()
g.parse("empty-graph.rdf")

# Определяем пространство имен
GAMES = Namespace("http://www.example.org/ontologies/videogames#")

# Добавляем жанры
for genre_name in genres:
    # Создаем URI для жанра (заменяем пробелы на подчеркивания)
    genre_uri = URIRef(GAMES[genre_name.replace(" ", "_")])
    
    # Добавляем жанр как экземпляр класса Genre
    g.add((genre_uri, RDF.type, GAMES.Genre))
    # Добавляем название жанра
    g.add((genre_uri, RDFS.label, Literal(genre_name)))

# Добавляем платформы
for platform_name in platforms:
    # Определяем тип платформы на основе имени
    if "PC" in platform_name:
        platform_class = GAMES.PCPlatform
    elif any(mobile in platform_name.lower() for mobile in ["android", "ios", "mobile"]):
        platform_class = GAMES.MobilePlatform
    else:
        platform_class = GAMES.Console
    
    # Создаем URI для платформы
    platform_uri = URIRef(GAMES[platform_name.replace(" ", "_")])
    
    # Добавляем платформу как экземпляр соответствующего класса
    g.add((platform_uri, RDF.type, platform_class))
    # Добавляем название платформы
    g.add((platform_uri, RDFS.label, Literal(platform_name)))

# Получаем игры
games_data = get_games()

# Улучшенная логика определения класса игры
def determine_game_class(game):
    # Проверяем теги для определения мультиплеера
    tags = [tag['name'].lower() for tag in game.get('tags', [])]
    
    # Проверяем на мультиплеер
    multiplayer_tags = ['multiplayer', 'co-op', 'cooperative', 'online multiplayer', 'local multiplayer']
    is_multiplayer = any(tag in tags for tag in multiplayer_tags)
    
    if is_multiplayer:
        # Проверяем на онлайн-игру
        online_tags = ['online multiplayer', 'mmo', 'online co-op', 'online']
        if any(tag in tags for tag in online_tags):
            return GAMES.OnlineGame
        return GAMES.CoopGame
    else:
        # Для одиночных игр проверяем популярность
        ratings_count = game.get('ratings_count', 0) or 0  # Обрабатываем None
        metacritic = game.get('metacritic') or 0  # Обрабатываем None
        
        if ratings_count > 10000 or metacritic > 75:
            return GAMES.PopularGame
        return GAMES.SinglePlayerGame

# В основном цикле обработки игр
for game in games_data:
    # Создаем URI для игры
    game_uri = URIRef(GAMES[game['slug'].replace("-", "_")])
    
    # Определяем тип игры используя новую функцию
    game_class = determine_game_class(game)
    
    # Добавляем игру как экземпляр соответствующего класса
    g.add((game_uri, RDF.type, game_class))
    
    # Добавляем название игры
    g.add((game_uri, RDFS.label, Literal(game['name'])))
    
    # Добавляем связи с жанрами (Object Property)
    for genre in game.get('genres', []):
        genre_uri = URIRef(GAMES[genre['name'].replace(" ", "_")])
        g.add((game_uri, GAMES.has_Genre, genre_uri))
    
    # Добавляем связи с платформами (Object Property)
    for platform in game.get('platforms', []):
        platform_uri = URIRef(GAMES[platform['platform']['name'].replace(" ", "_")])
        g.add((game_uri, GAMES.has_Platform, platform_uri))
    
    # Добавляем Data Properties
    if 'released' in game and game['released']:
        g.add((game_uri, GAMES.release_Year, Literal(game['released'][:4], datatype=XSD.integer)))
    
    if 'esrb_rating' in game and game['esrb_rating'] is not None and isinstance(game['esrb_rating'], dict):
        g.add((game_uri, GAMES.age_rating, Literal(game['esrb_rating'].get('name', 'Not rated'))))
    else:
        g.add((game_uri, GAMES.age_rating, Literal('Not rated')))
    
    if 'playtime' in game:
        g.add((game_uri, GAMES.avg_play_time, Literal(game['playtime'], datatype=XSD.integer)))
    
    # Новые Data Properties
    if 'rating' in game:
        g.add((game_uri, GAMES.rating, Literal(game['rating'], datatype=XSD.float)))
    
    if 'metacritic' in game:
        g.add((game_uri, GAMES.metacritic_score, Literal(game['metacritic'], datatype=XSD.integer)))
    
    if 'description' in game:
        g.add((game_uri, GAMES.description, Literal(game['description'])))
    
    if 'developers' in game and game['developers']:
        g.add((game_uri, GAMES.developer, Literal(game['developers'][0]['name'])))
    
    if 'publishers' in game and game['publishers']:
        g.add((game_uri, GAMES.publisher, Literal(game['publishers'][0]['name'])))
    
    # Существующие булевы свойства
    g.add((game_uri, GAMES.is_multiplayer, Literal(game.get('multiplayer', False), datatype=XSD.boolean)))
    g.add((game_uri, GAMES.online, Literal(
        any('online' in tag['name'].lower() for tag in game.get('tags', [])), 
        datatype=XSD.boolean
    )))
    
    # Добавляем максимальное количество игроков (если доступно)
    if 'max_players' in game:
        g.add((game_uri, GAMES.max_players, Literal(game.get('max_players', 1), datatype=XSD.integer)))

# Сохраняем обновленную онтологию
g.serialize(destination="updated_ontology2.owl", format="xml")


