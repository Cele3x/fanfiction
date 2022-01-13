# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from itemadapter import ItemAdapter
from fanfiction.items import User, Story
from fanfiction.utilities import merge_dict
from datetime import datetime


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
        self.db['fandoms'].drop()
        self.db['characters'].drop()
        self.db['story_topics'].drop()
        self.db['story_characters'].drop()
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
        if 'source' in item:
            source = self.db['sources'].find_one({'name': item['source']})
            if source:
                item['sourceId'] = source['_id']
            del item['source']

        # set category
        if 'category' in item:
            category = self.db['categories'].find_one({'$or': [{'name1': item['category']}, {'name2': item['category']}, {'name3': item['category']}]})
            if category:
                item['categoryId'] = category['_id']
            else:
                item['categoryId'] = self.db['categories'].insert_one({'name1': item['category'], 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
            del item['category']

        # set genre
        if 'genre' in item:
            genre = self.db['genres'].find_one({'$or': [{'name1': item['genre']}, {'name2': item['genre']}, {'name3': item['genre']}]})
            if genre:
                item['genreId'] = genre['_id']
            else:
                item['genreId'] = self.db['genres'].insert_one({'name1': item['genre'], 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
            del item['genre']

        # set fandom
        if 'fandom' in item:
            fandom = self.db['fandoms'].find_one({'genreId': item['genreId'], '$or': [{'name1': item['fandom']}, {'name2': item['fandom']}, {'name3': item['fandom']}]})
            if fandom:
                item['fandomId'] = fandom['_id']
            else:
                item['fandomId'] = self.db['fandoms'].insert_one({'genreId': item['genreId'], 'name1': item['fandom'], 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
            del item['fandom']

        # set rating
        if 'rating' in item:
            rating = self.db['ratings'].find_one({'$or': [{'name1': item['rating']}, {'name2': item['rating']}, {'name3': item['rating']}]})
            if rating:
                item['ratingId'] = rating['_id']
            else:
                item['ratingId'] = self.db['ratings'].insert_one({'name1': item['rating'], 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
            del item['rating']

        # set pairing
        if 'pairing' in item:
            pairing = self.db['pairings'].find_one({'$or': [{'name1': item['pairing']}, {'name2': item['pairing']}, {'name3': item['pairing']}]})
            if pairing:
                item['pairingId'] = pairing['_id']
            else:
                item['pairingId'] = self.db['pairings'].insert_one({'name1': item['pairing'], 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
            del item['pairing']

        # search for existing user and set authorId if found or create a rudimentary user
        # user = self.db['users'].find_one_and_update({'name': item['author']}, {'$setOnInsert': {'name': item['author']}}, {'upsert': 'true', 'returnDocument': 'after'})
        # TODO: sometimes there is an age verification required (e.g.: https://www.fanfiktion.de/s/5ead3b92000482001d06c2b9/1/Children-of-Chemos-King) -> crawl between 11pm-4am
        user = self.db['users'].find_one({'url': item['authorUrl']})
        if user:
            item['authorId'] = user['_id']
        else:
            item['authorId'] = self.process_user(User({'url': item['authorUrl']}))
        del item['authorUrl']

        # exclude item keys that are processed later
        excluded_keys = ['topics', 'characters']
        story_item = {k: item[k] for k in set(list(item.keys())) - set(excluded_keys)}
        # check if story already exists
        story = self.db['stories'].find_one({'url': story_item['url']})
        if story:  # merge and update story
            story_item['updatedAt'] = datetime.utcnow()
            updated_story = merge_dict(story, story_item)
            story_id = self.db['stories'].update_one({'_id': story['_id']}, {'$set': updated_story})
        else:  # create new story
            story_item['createdAt'] = datetime.utcnow()
            story_item['updatedAt'] = datetime.utcnow()
            story_id = self.db['stories'].insert_one(story_item).inserted_id

        # set topics for story
        if 'topics' in item:
            for t in item['topics'].split(', '):
                topic = self.db['topics'].find_one({'$or': [{'name1': t}, {'name2': t}, {'name3': t}]})
                if topic:
                    topic_id = topic['_id']
                else:
                    topic_id = self.db['topics'].insert_one({'name1': t}).inserted_id
                # check if topic already exists for story
                story_topic = self.db['story_topics'].find_one({'storyId': story_id, 'topicId': topic_id})
                if story_topic is None:
                    self.db['story_topics'].insert_one({'storyId': story_id, 'topicId': topic_id, 'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()})
            del item['topics']

        # set characters for story
        if 'characters' in item:
            for c in item['characters'].split(', '):
                fandom_id = item['fandomId'] if 'fandomId' in item else None
                character = self.db['characters'].find_one({'fandomId': fandom_id, '$or': [{'name1': c}, {'name2': c}, {'name3': c}]})
                if character:
                    character_id = character['_id']
                else:
                    character_id = self.db['characters'].insert_one({'fandomId': fandom_id, 'name1': c, 'name2': None, 'name3': None}).inserted_id
                # check if character already exists for story
                story_characters = self.db['story_characters'].find_one({'storyId': story_id, 'characterId': character_id})
                if story_characters is None:
                    self.db['story_characters'].insert_one({'storyId': story_id, 'characterId': character_id, 'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()})
            del item['characters']

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
