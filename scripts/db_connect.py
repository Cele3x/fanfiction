#!/usr/bin/python3

# -----------------------------------------------------------
# Provides functions for connecting to and disconnecting from
# a MongoDB database while using environment specific
# variables.
# -----------------------------------------------------------

import os
import pymongo
from dotenv import load_dotenv
import urllib.parse
from typing import Optional
from pymongo.database import Database

load_dotenv('../.env')

MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)

client = pymongo.MongoClient(MONGO_URI)


def get_database(db_name: Optional[str] = MONGO_DB) -> Database:
    return client[db_name]


def disconnect() -> None:
    client.close()
