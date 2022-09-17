#!/usr/bin/python3

# -----------------------------------------------------------
# Compares FF and AO3 fandoms and tries to match those
# storing them in a CSV file.
# -----------------------------------------------------------

import os
import urllib.parse
import pymongo
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import re
import csv

load_dotenv('../.env')

MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)

client = pymongo.MongoClient(MONGO_URI)
db = client['FanFiction']
f = open('fandoms.csv', 'w', encoding='UTF8')

try:
    writer = csv.writer(f)
    writer.writerow(['Genre', 'AO3', 'FF', 'Score', 'AO3-Cleansed', 'FF-Cleansed'])

    genres = db.stories.distinct('genre')
    # 07-Ghost  <->  07 Ghost  =>  88
    # ??? - Fandom  <->  Die drei ???  =>  35
    # Akatsuki no Yona | Yona of the Dawn  <->  Akatsuki no Yona  =>  65
    for genre in genres:
        fandoms_ao3 = list(db.stories.aggregate([
            {"$match": {"source": 'ArchiveOfOurOwn', 'genre': genre}},
            {"$unwind": "$fandoms"},
            {"$group": {"_id": None, "ffs": {"$addToSet": "$fandoms"}}},
            {"$unwind": "$ffs"},
            {"$sort": {"ffs": 1}},
            {"$project": {"_id": 0, "name": "$ffs"}}
        ]))
        fandoms_ff = list(db.stories.aggregate([
            {"$match": {"source": 'FanFiktion', 'genre': genre}},
            {"$unwind": "$fandoms"},
            {"$group": {"_id": None, "ffs": {"$addToSet": "$fandoms"}}},
            {"$unwind": "$ffs"},
            {"$sort": {"ffs": 1}},
            {"$project": {"_id": 0, "name": "$ffs"}}
        ]))
        for fandom_ao3 in fandoms_ao3:
            best_ratio = 0
            best_match = ''
            best_match_cleansed = ''
            pattern = r'\sffs?|\smmfs?|\sfandom|\(.*\)|[:\|]'
            s1 = fandom_ao3['name'].lower()
            s1 = re.sub(pattern, ' ', s1)
            s1 = ' '.join(s1.split())
            for fandom_ff in fandoms_ff:
                s2 = fandom_ff['name'].lower()
                s2 = re.sub(pattern, ' ', s2)
                s2 = ' '.join(s2.split())
                ratio = fuzz.ratio(s1, s2)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = fandom_ff['name']
                    best_match_cleansed = s2
            if best_match != '' and 0 < best_ratio < 100:
                writer.writerow([genre, fandom_ao3['name'], best_match, best_ratio, s1, best_match_cleansed])
                print(fandom_ao3['name'], ' <-> ', best_match, ' => ', best_ratio)

finally:
    f.close()
    client.close()
