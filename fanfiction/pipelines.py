# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from itemadapter import ItemAdapter
from fanfiction.items import User, Story
from fanfiction.utilities import merge_dict


class FanfictionPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.db = None
        self.client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB', 'items')
        )

    def open_spider(self, _spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # truncate database
        self.db['users'].delete_many({})
        self.db['stories'].delete_many({})

    def close_spider(self, _spider):
        self.client.close()

    # determine type of item and call its save function accordingly
    def process_item(self, item, _spider):
        # author = item.pop('author')
        # user_id = self.db['users'].insert_one(author).inserted_id
        if isinstance(item, User):
            return self.process_user(item)
        elif isinstance(item, Story):
            return self.process_story(item)
        return item

    # save story to database
    def process_story(self, item):
        # convert story item to dictionary
        item = ItemAdapter(item).asdict()
        # search for existing user and set authorId if found or create a rudimentary user
        # user = self.db['users'].find_one_and_update({'name': item['author']}, {'$setOnInsert': {'name': item['author']}}, {'upsert': 'true', 'returnDocument': 'after'})
        # TODO: somethimes there is an age verification required (e.g.: https://www.fanfiktion.de/s/5ead3b92000482001d06c2b9/1/Children-of-Chemos-King)
        user = self.db['users'].find_one({'url': item['authorUrl']})
        if user:
            item['authorId'] = user['_id']
        else:
            item['authorId'] = self.process_user(User({'url': item['authorUrl']}))
        del item['authorUrl']
        # check if story already exists
        story = self.db['stories'].find_one({'url': item['url']})
        if story:
            updated_story = merge_dict(story, item)
            self.db['stories'].update_one({'_id': story['_id']}, {'$set': updated_story})
        else:
            self.db['stories'].insert_one(item)

    # save user to database
    def process_user(self, item):
        item = ItemAdapter(item).asdict()
        # check if user already exists
        user = self.db['users'].find_one({'url': item['url']})
        if user:
            updated_user = merge_dict(user, item)
            self.db['users'].update_one({'_id': user['_id']}, {'$set': updated_user})
            return user['_id']
        else:
            return self.db['users'].insert_one(item).inserted_id
