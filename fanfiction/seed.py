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
    {'name1': 'Anime & Manga', 'name2': '', 'name3': ''},
    {'name1': 'Bücher', 'name2': 'Books', 'name3': ''},
    {'name1': 'Cartoons & Comics', 'name2': '', 'name3': ''},
    {'name1': 'Computerspiele', 'name2': '', 'name3': ''},
    {'name1': 'Crossover', 'name2': '', 'name3': ''},
    {'name1': 'Kino- & TV-Filme', 'name2': '', 'name3': ''},
    {'name1': 'Musicals', 'name2': '', 'name3': ''},
    {'name1': 'Prominente', 'name2': '', 'name3': ''},
    {'name1': 'Serien & Prodcasts', 'name2': '', 'name3': ''},
    {'name1': 'Tabletop- & Rollenspiele', 'name2': '', 'name3': ''},
]
db['genres'].insert_many(genres)

# TOPICS
db['topics'].drop()
topics = [
    {'name1': 'Abenteuer', 'name2': 'Adventure', 'name3': ''},
    {'name1': 'Action', 'name2': '', 'name3': ''},
    {'name1': 'Allgemein', 'name2': '', 'name3': ''},
    {'name1': 'Angst', 'name2': '', 'name3': ''},
    {'name1': 'Drama', 'name2': '', 'name3': ''},
    {'name1': 'Erotik', 'name2': '', 'name3': ''},
    {'name1': 'Familie', 'name2': '', 'name3': ''},
    {'name1': 'Fantasy', 'name2': '', 'name3': ''},
    {'name1': 'Freundschaft', 'name2': '', 'name3': ''},
    {'name1': 'Historisch', 'name2': '', 'name3': ''},
    {'name1': 'Horror', 'name2': '', 'name3': ''},
    {'name1': 'Humor', 'name2': '', 'name3': ''},
    {'name1': 'Krimi', 'name2': '', 'name3': ''},
    {'name1': 'Liebesgeschichte', 'name2': '', 'name3': ''},
    {'name1': 'Mistery', 'name2': '', 'name3': ''},
    {'name1': 'Parodie', 'name2': '', 'name3': ''},
    {'name1': 'Poesie', 'name2': '', 'name3': ''},
    {'name1': 'Romance', 'name2': '', 'name3': ''},
    {'name1': 'Schmerz/Trost', 'name2': '', 'name3': ''},
    {'name1': 'Sci-Fi', 'name2': '', 'name3': ''},
    {'name1': 'Suspense', 'name2': '', 'name3': ''},
    {'name1': 'Thriller', 'name2': '', 'name3': ''},
    {'name1': 'Tragödie', 'name2': '', 'name3': ''},
    {'name1': 'Übernatürlich', 'name2': '', 'name3': ''},
]
db['topics'].insert_many(topics)

# RATINGS
db['ratings'].drop()
ratings = [
    {'name1': 'P6', 'name2': '', 'name3': ''},
    {'name1': 'P12', 'name2': '', 'name3': ''},
    {'name1': 'P16', 'name2': '', 'name3': ''},
    {'name1': 'P18', 'name2': '', 'name3': ''},
    {'name1': 'P18-AVL', 'name2': '', 'name3': ''},
]
db['ratings'].insert_many(ratings)

# PAIRINGS
db['pairings'].drop()
pairings = [
    {'name1': 'Gen', 'name2': '', 'name3': ''},
    {'name1': 'Het', 'name2': '', 'name3': ''},
    {'name1': 'MaleSlash', 'name2': '', 'name3': ''},
    {'name1': 'FemSlash', 'name2': '', 'name3': ''},
    {'name1': 'Mix', 'name2': '', 'name3': ''},
    {'name1': 'Div', 'name2': '', 'name3': ''},
]
db['pairings'].insert_many(pairings)

# FANDOMS
db['fandoms'].drop()
fandoms = [
    {'name1': 'Harry Potter', 'name2': '', 'name3': ''},
]
db['fandoms'].insert_many(fandoms)

