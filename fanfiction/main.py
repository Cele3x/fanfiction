from scrapy import cmdline
from settings import MONGO_URI, MONGO_DB
from pymongo import MongoClient

# connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB]
#
# # drop dynamic collections that are not prefilled with seed data
# static_collections = ['sources', 'genres', 'categories', 'topics', 'ratings', 'pairings']
# dynamic_collections = db.list_collection_names(filter={'name': {'$nin': static_collections}})
# for collection in dynamic_collections:
#     db[collection].drop()
#
# # close client
# client.close()

cmdline.execute('scrapy crawl FanFiktion'.split())

# for pausing and resuming crawls
# when pausing this crawl, resume it with the same command
# YOU HAVE TO WAIT FOR CLOSING THE JOB WITH JUST ONE CTRL-C (FORCING WON'T WORK)!
# cmdline.execute('scrapy crawl FanFiktion -s JOBDIR=crawls/FanFiktion-1'.split())
