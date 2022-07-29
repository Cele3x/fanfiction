#!/usr/bin/python3

import os
import pymongo
from dotenv import load_dotenv
import urllib.parse

load_dotenv('../.env')

MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)
EXTRACTED_REVIEWS_PATH = os.environ.get('EXTRACTED_REVIEWS_PATH')

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

for root, dirs, files in os.walk(EXTRACTED_REVIEWS_PATH):
    for filename in files:
        if not filename.endswith('.html'):
            continue
        fullpath = os.path.join(root, filename)
        print(fullpath)
        parent_dir = fullpath.split(os.path.sep)[-2]
        reviews = db['csv_reviews'].find_one({'filename': filename})
        if reviews:
            print(parent_dir, '/', fullpath)
            db['csv_reviews'].update_one({'_id': reviews['_id']}, {'$set': {'extracted_folder': parent_dir}})
        else:
            print(parent_dir, '/', fullpath)
            parts = filename.split('_')  # 4f36ea8000016c470670b798_date_0_4.html
            uid = parts[0]
            sorted_by = parts[1]
            chapter = parts[2]
            page = parts[3].split('.')[0]
            url = 'https://www.fanfiktion.de/r/s/' + uid + '/' + sorted_by + '/' + chapter + '/' + page
            db['csv_reviews'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': parent_dir, 'page': page})

client.close()
