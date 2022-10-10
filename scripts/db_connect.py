#!/usr/bin/python3

# -----------------------------------------------------------
# Provides functions for connecting to and disconnecting from
# a MongoDB database while using environment specific
# variables.
# -----------------------------------------------------------

import os
from typing import Union

import pymongo
from dotenv import load_dotenv
import urllib.parse
from pymongo.database import Database


def get_mongo_uri() -> Union[str, bool]:
    try:
        load_dotenv()
        user = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
        pw = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
        host = os.environ.get('MONGO_HOST')
        port = os.environ.get('MONGO_PORT')
        print('Mongo-URI: %s@%s:%s' % (user, host, port))
        return 'mongodb://%s:%s@%s:%s' % (user, pw, host, port)
    except Exception as e:
        print(e)
        return False


class DatabaseConnection:

    def __init__(self):
        self.uri = get_mongo_uri()
        self.client = None

    def connect(self, database_name: str) -> Union[Database, bool]:
        try:
            self.client = pymongo.MongoClient(self.uri)
            return self.client[database_name]
        except Exception as e:
            print(e)
            return False

    def disconnect(self) -> bool:
        try:
            self.client.close()
            return True
        except Exception as e:
            print(e)
            return False
