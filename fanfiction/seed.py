from settings import MONGO_URI, MONGO_DB
from pymongo import MongoClient
from datetime import datetime

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
    {'name1': 'Serien & Prodcasts', 'name2': None, 'name3': None},
    {'name1': 'Tabletop- & Rollenspiele', 'name2': None, 'name3': None},
]
db['genres'].insert_many(genres)

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

# FANDOMS
# db['fandoms'].drop()
# fandoms = [
#     {'genreId': None, 'name1': 'Harry Potter', 'name2': None, 'name3': None},
# ]
# db['fandoms'].insert_many(fandoms)

