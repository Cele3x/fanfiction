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
from pymongo.client_session import ClientSession


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
        self.database = None

    def connect(self, database_name: str) -> Union[Database, bool]:
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.database = self.client[database_name]
            return self.database
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

    def start_session(self) -> ClientSession:
        try:
            return self.client.start_session()
        except Exception as e:
            print(e)

    def refresh_session(self, session_id: [str, any]):
        try:
            self.client.admin.command({'refreshSessions': [session_id]})
        except Exception as e:
            print(e)
