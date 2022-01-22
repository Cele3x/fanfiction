# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import re
from typing import Union
from datetime import datetime
from itemadapter import ItemAdapter
from fanfiction.items import User, Story, Chapter
from fanfiction.utilities import merge_dict


class FanfictionPipeline:

    def __init__(self, mongo_uri: str, mongo_db: str):
        """Initializes FanFiction pipeline.

        :param mongo_uri: str
            Uri to MongoDB database
        :param mongo_db: str
            Name of MongoDB database
        """
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
        """Connects to MongoDB and drops all existing collections containing dynamic data.

        :param _spider: Any
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, _spider):
        """Disconnects from MongoDB when done with current spider.

        :param _spider: Any
        """
        self.client.close()

    def process_item(self, item: Union[User, Story, Chapter], _spider):
        """Determines the type of item and calls its save function accordingly.
        Return value with e.g. a user ID cannot be used since function calls are asynchronous.

        :param item: User | Story
            The item object to process
        :param _spider: Any
            The currently processed spider
        """
        if isinstance(item, User):
            return self.process_user(item)
        elif isinstance(item, Story):
            return self.process_story(item)
        elif isinstance(item, Chapter):
            return self.process_chapter(item)
        else:
            print('Passed item object is not type of the allowed types!')

    def process_story(self, item: Story):
        """Save Story object to the database.

        :param item: Story
        """
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
        excluded_keys = ['topics', 'characters', 'chapterNumber', 'chapterTitle', 'chapterContent', 'chapterNotes', 'chapterPublishedOn', 'chapterReviewedOn']
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

        # # set chapter items
        # # check if chapter already exists for story
        # if 'chapterContent' in item:
        #     chapter = self.db['chapters'].find_one({'storyId': story_id, 'number': item['chapterNumber']})
        #     if chapter is None:
        #         self.db['chapters'].insert_one({'story_id': story_id, 'number': item['chapterNumber'], 'title': item['chapterTitle'],
        #                                         'content': item['chapterContent'], 'notes': None, 'publishedOn': None, 'reviewedOn': None,
        #                                         'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()})

    def process_chapter(self, item: Chapter):
        """Save Chapter object to database.

        :param item: Chapter
        """
        item = ItemAdapter(item).asdict()
        # check if chapter already exists
        story_url = re.sub(r'/\d+/', '/1/', item['storyUrl'])
        story = self.db['stories'].find_one({'url': story_url})
        if story and 'number' in item:
            item['storyId'] = story['_id']
            chapter = self.db['chapters'].find_one({'storyId': story['_id'], 'number': item['number']})
            if chapter:  # merge and update chapter
                item['updatedAt'] = datetime.utcnow()
                updated_chapter = merge_dict(chapter, item)
                self.db['chapters'].update_one({'_id': chapter['_id']}, {'$set': updated_chapter})
            else:  # create new chapter
                item['createdAt'] = datetime.utcnow()
                item['updatedAt'] = datetime.utcnow()
                self.db['chapters'].insert_one(item)

    def process_user(self, item: User):
        """Save User object to the database.

        :param item: User
        """
        item = ItemAdapter(item).asdict()
        # check if user already exists
        user = self.db['users'].find_one({'url': item['url']})
        if user:
            updated_user = merge_dict(user, item)
            self.db['users'].update_one({'_id': user['_id']}, {'$set': updated_user})
            return user['_id']
        else:
            return self.db['users'].insert_one(item).inserted_id
