#!/usr/bin/python3

# -----------------------------------------------------------
# Reusable database connection for scripts
# -----------------------------------------------------------

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

client = pymongo.MongoClient(MONGO_URI)


def db():
    return client[MONGO_DB]


def disconnect():
    client.close()
