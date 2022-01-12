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
        # drop collections
        self.db['users'].drop()
        self.db['stories'].drop()

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

        # set story source
        if 'sourceName' in item:
            source = self.db['sources'].find_one({'name': item['sourceName']})
            if source:
                item['sourceId'] = source['_id']
            del item['sourceName']

        # set genre
        if 'genreName' in item:
            genre = self.db['genres'].find_one({'$or': [{'name1': item['genreName']}, {'name2': item['genreName']}, {'name3': item['genreName']}]})
            if genre:
                item['genreId'] = genre['_id']
            else:
                item['genreId'] = self.db['genres'].insert_one({'name1': item['genreName']}).inserted_id
            del item['genreName']

        # set fandom
        if 'fandomName' in item:
            fandom = self.db['fandoms'].find_one({'genreId': item['genreId'], '$or': [{'name1': item['fandomName']}, {'name2': item['fandomName']}, {'name3': item['fandomName']}]})
            if fandom:
                item['fandomId'] = fandom['_id']
            else:
                item['fandomId'] = self.db['fandoms'].insert_one({'genreId': item['genreId'], 'name1': item['fandomName']}).inserted_id
            del item['fandomName']

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
        if story:  # merge and update story
            updated_story = merge_dict(story, item)
            self.db['stories'].update_one({'_id': story['_id']}, {'$set': updated_story})
        else:  # create new story
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
