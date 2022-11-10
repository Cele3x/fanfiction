from settings import MONGO_URI, MONGO_DB
from pymongo import MongoClient

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# SOURCES
db['sources'].drop()
sources = [
    {'name': 'FanFiktion', 'url': 'https://www.fanfiktion.de/'},
]
db['sources'].insert_many(sources)

# GENRES TODO: maybe split up for other sources
db['genres'].drop()
genres = [
    {'name1': 'Anime & Manga', 'name2': None, 'name3': None},
    {'name1': 'Bücher', 'name2': 'Books', 'name3': None},
    {'name1': 'Cartoons & Comics', 'name2': None, 'name3': None},
    {'name1': 'Computerspiele', 'name2': None, 'name3': None},
    {'name1': 'Crossover', 'name2': None, 'name3': None},
    {'name1': 'Kino- & TV-Filme', 'name2': None, 'name3': None},
    {'name1': 'Musicals', 'name2': None, 'name3': None},
    {'name1': 'Prominente', 'name2': None, 'name3': None},
    {'name1': 'Serien & Podcasts', 'name2': None, 'name3': None},
    {'name1': 'Tabletop- & Rollenspiele', 'name2': None, 'name3': None},
]
db['genres'].insert_many(genres)

# CATEGORIES
db['categories'].drop()
categories = [
    {'name1': 'Aufzählung/Liste', 'name2': None, 'name3': None},
    {'name1': 'Chat/Interview/Quiz', 'name2': None, 'name3': None},
    {'name1': 'Crossover', 'name2': None, 'name3': None},
    {'name1': 'Drabble', 'name2': None, 'name3': None},
    {'name1': 'Gedicht', 'name2': None, 'name3': None},
    {'name1': 'Geschichte', 'name2': None, 'name3': None},
    {'name1': 'Kurzgeschichte', 'name2': None, 'name3': None},
    {'name1': 'Leseprobe', 'name2': None, 'name3': None},
    {'name1': 'Liedtext', 'name2': None, 'name3': None},
    {'name1': 'Mitmachgeschichte', 'name2': None, 'name3': None},
    {'name1': 'Oneshot', 'name2': None, 'name3': None},
    {'name1': 'Sammlung', 'name2': None, 'name3': None},
    {'name1': 'Songfic', 'name2': None, 'name3': None},
]
db['categories'].insert_many(categories)

# TOPICS
db['topics'].drop()
topics = [
    {'name1': 'Abenteuer', 'name2': 'Adventure', 'name3': None},
    {'name1': 'Action', 'name2': None, 'name3': None},
    {'name1': 'Allgemein', 'name2': None, 'name3': None},
    {'name1': 'Angst', 'name2': None, 'name3': None},
    {'name1': 'Drama', 'name2': None, 'name3': None},
    {'name1': 'Erotik', 'name2': None, 'name3': None},
    {'name1': 'Familie', 'name2': None, 'name3': None},
    {'name1': 'Fantasy', 'name2': None, 'name3': None},
    {'name1': 'Freundschaft', 'name2': None, 'name3': None},
    {'name1': 'Historisch', 'name2': None, 'name3': None},
    {'name1': 'Horror', 'name2': None, 'name3': None},
    {'name1': 'Humor', 'name2': None, 'name3': None},
    {'name1': 'Krimi', 'name2': None, 'name3': None},
    {'name1': 'Liebesgeschichte', 'name2': None, 'name3': None},
    {'name1': 'Mistery', 'name2': None, 'name3': None},
    {'name1': 'Parodie', 'name2': None, 'name3': None},
    {'name1': 'Poesie', 'name2': None, 'name3': None},
    {'name1': 'Romance', 'name2': None, 'name3': None},
    {'name1': 'Schmerz/Trost', 'name2': None, 'name3': None},
    {'name1': 'Sci-Fi', 'name2': None, 'name3': None},
    {'name1': 'Suspense', 'name2': None, 'name3': None},
    {'name1': 'Thriller', 'name2': None, 'name3': None},
    {'name1': 'Tragödie', 'name2': None, 'name3': None},
    {'name1': 'Übernatürlich', 'name2': None, 'name3': None},
]
db['topics'].insert_many(topics)

# RATINGS
db['ratings'].drop()
ratings = [
    {'name1': 'P6', 'name2': None, 'name3': None},
    {'name1': 'P12', 'name2': None, 'name3': None},
    {'name1': 'P16', 'name2': None, 'name3': None},
    {'name1': 'P18', 'name2': None, 'name3': None},
    {'name1': 'P18-AVL', 'name2': None, 'name3': None},
]
db['ratings'].insert_many(ratings)

# PAIRINGS
db['pairings'].drop()
pairings = [
    {'name1': 'Gen', 'name2': None, 'name3': None},
    {'name1': 'Het', 'name2': None, 'name3': None},
    {'name1': 'MaleSlash', 'name2': None, 'name3': None},
    {'name1': 'FemSlash', 'name2': None, 'name3': None},
    {'name1': 'Mix', 'name2': None, 'name3': None},
    {'name1': 'Div', 'name2': None, 'name3': None},
]
db['pairings'].insert_many(pairings)

db['chapters'].create_index({'url': 1})
db['chapters'].create_index({'storyId': 1})
db['characters'].create_index({'fandomId': 1})
db['reviews'].create_index({'parentId': 1})
db['reviews'].create_index({'reviewableId': 1, 'reviewableType': 1})
db['reviews'].create_index({'userId': 1})
db['stories'].create_index({'categoryId': 1})
db['stories'].create_index({'genreId': 1})
db['stories'].create_index({'pairingId': 1})
db['stories'].create_index({'ratingId': 1})
db['stories'].create_index({'url': 1})
db['stories'].create_index({'ageVerification': 1})
db['stories'].create_index({'isPreliminary': 1})
db['stories'].create_index({'authorId': 1})
db['stories'].create_index({'sourceId': 1})
db['story_characters'].create_index({'characterId': 1, 'storyId': 1})
db['story_fandoms'].create_index({'fandomId': 1, 'storyId': 1})
db['story_topics'].create_index({'topicId': 1, 'storyId': 1})
db['users'].create_index({'url': 1})
db['users'].create_index({'sourceId': 1})

client.close()

