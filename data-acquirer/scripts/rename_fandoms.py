#!/usr/bin/python3

# -----------------------------------------------------------
# Uses the CSV file generated in match_fandoms.py to rename
# AO3 fandoms matching the FF names.
# -----------------------------------------------------------

import os
import urllib.parse
from time import sleep

import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import re
import csv

load_dotenv('../../.env')

MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)

client = pymongo.MongoClient(MONGO_URI)
db = client['FanfictionDB']

try:
    genres = db.genres.find({})
    for genre in genres:
        with open('fandoms.csv', 'r', encoding='UTF8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                fandom_ao3 = db.fandoms.find_one({'genreId': genre['_id'], 'name1': row[2], 'sourceIds': [ObjectId('628b6defe477107a10d9f5f1')]})
                if fandom_ao3 and (row[1] == '1' or row[1] == '2'):
                    fandom_ff = db.fandoms.find_one({'genreId': genre['_id'], 'name1': row[3], 'sourceIds': [ObjectId('61e012e24092d5872dc0a716')]})
                    if fandom_ff:
                        print('Renaming %s => %s' % (row[2], row[3]))
                        fandom_ff_id = fandom_ff['_id']
                        db.fandoms.update_one({'_id': fandom_ff_id}, {'$addToSet': {'names': row[2], 'sourceIds': ObjectId('628b6defe477107a10d9f5f1')}})
                    else:
                        print('New fandom %s' % (row[3]))
                        fandom_ff_id = db.fandoms.insert_one({'genreId': genre['_id'], 'name1': row[3], 'sourceIds': [ObjectId('628b6defe477107a10d9f5f1')]}).inserted_id
                    db.story_fandoms.update_many({'fandomId': fandom_ao3['_id']}, {'$set': {'fandomId': fandom_ff_id}})
                    db.fandoms.delete_one({'_id': fandom_ao3['_id']})
finally:
    client.close()
