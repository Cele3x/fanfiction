# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from typing import Union
from datetime import datetime
from itemadapter import ItemAdapter
from fanfiction.items import User, Story, Chapter, Review
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
        elif isinstance(item, Review):
            return self.process_review(item)
        else:
            print('Passed item object is not type of the allowed types!')

    def process_story(self, item: Story, is_preliminary=False) -> [str, None]:
        """Save Story object to the database.

        :return: id of updated or created story or None
        :param item: Story
        :param is_preliminary: Boolean indicating if the reason for creating the story is for association purposes
        """
        # convert story item to dictionary
        item = ItemAdapter(item).asdict()
        item['isPreliminary'] = is_preliminary

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
        if 'authorUrl' in item:
            user = self.db['users'].find_one({'url': item['authorUrl']})
            if user:
                item['authorId'] = user['_id']
            else:
                item['authorId'] = self.process_user(User({'url': item['authorUrl']}), True)
            del item['authorUrl']

        # exclude item keys that are processed later
        excluded_keys = ['fandoms', 'topics', 'characters']
        story_item = {k: item[k] for k in set(list(item.keys())) - set(excluded_keys)}
        if 'url' in story_item:
            if 'likes' in story_item and story_item['likes']:
                story_item['likes'] = int(story_item['likes'])
            if 'follows' in story_item and story_item['follows']:
                story_item['follows'] = int(story_item['follows'])
            if 'hits' in story_item and story_item['hits']:
                story_item['hits'] = int(story_item['hits'])
            # check if story already exists
            story = self.db['stories'].find_one({'url': story_item['url']})
            if story:  # merge and update story
                story_item['updatedAt'] = datetime.utcnow()
                updated_story = merge_dict(story, story_item)
                self.db['stories'].update_one({'_id': story['_id']}, {'$set': updated_story})
                story_id = story['_id']
            else:  # create new story
                story_item['createdAt'] = datetime.utcnow()
                story_item['updatedAt'] = datetime.utcnow()
                story_id = self.db['stories'].insert_one(story_item).inserted_id
        else:
            return None

        # set fandoms for story
        fandom_id = None
        if 'fandoms' in item:
            for f in item['fandoms'].split(', '):
                fandom = self.db['fandoms'].find_one({'$or': [{'name1': f}, {'name2': f}, {'name3': f}]})
                if fandom:
                    fandom_id = fandom['_id']
                else:
                    fandom_id = self.db['fandoms'].insert_one({'name1': f, 'name2': None, 'name3': None, 'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()}).inserted_id
                # check if fandom already exists for story
                story_fandom = self.db['story_fandoms'].find_one({'storyId': story_id, 'fandomId': fandom_id})
                if story_fandom is None:
                    self.db['story_fandoms'].insert_one({'storyId': story_id, 'fandomId': fandom_id, 'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()})
            del item['fandoms']

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
                character = self.db['characters'].find_one({'fandomId': fandom_id, '$or': [{'name1': c}, {'name2': c}, {'name3': c}]})
                if character:
                    character_id = character['_id']
                else:
                    character_id = self.db['characters'].insert_one({'fandomId': fandom_id, 'name1': c, 'name2': None, 'name3': None, 'createdAt': datetime.now(), 'updatedAt': datetime.now()}).inserted_id
                # check if character already exists for story
                story_characters = self.db['story_characters'].find_one({'storyId': story_id, 'characterId': character_id})
                if story_characters is None:
                    self.db['story_characters'].insert_one({'storyId': story_id, 'characterId': character_id, 'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()})
            del item['characters']
        return story_id

    def process_chapter(self, item: Chapter, is_preliminary=False) -> [str, None]:
        """Save Chapter object to database.

        :return: id of updated or created chapter
        :param item: Chapter
        :param is_preliminary: Boolean indicating if the reason for creating the user is for association purposes
        """
        item = ItemAdapter(item).asdict()
        item['isPreliminary'] = is_preliminary

        if 'storyUrl' in item:
            # check if story already exists
            story = self.db['stories'].find_one({'url': item['storyUrl']})
            if story:
                item['storyId'] = story['_id']
            else:
                item['storyId'] = self.process_story(Story({'url': item['storyUrl']}), True)
            del item['storyUrl']

        if 'url' in item:
            if 'number' in item and item['number']:
                item['number'] = int(item['number'])
            # check if chapter already exists
            chapter = self.db['chapters'].find_one({'url': item['url']})
            if chapter:  # merge and update chapter
                item['updatedAt'] = datetime.utcnow()
                updated_chapter = merge_dict(chapter, item)
                self.db['chapters'].update_one({'_id': chapter['_id']}, {'$set': updated_chapter})
                return chapter['_id']
            else:  # create new chapter
                item['createdAt'] = datetime.utcnow()
                item['updatedAt'] = datetime.utcnow()
                return self.db['chapters'].insert_one(item).inserted_id
        return None

    def process_user(self, item: User, is_preliminary=False) -> [str, None]:
        """Save User object to the database.

        :return: id of updated or created user
        :param item: User
        :param is_preliminary: Boolean indicating if the reason for creating the user is for association purposes
        """

        item = ItemAdapter(item).asdict()
        item['isPreliminary'] = is_preliminary

        # set user source
        if 'source' in item:
            source = self.db['sources'].find_one({'name': item['source']})
            if source:
                item['sourceId'] = source['_id']
            del item['source']

        if 'url' in item:
            # check if user already exists
            user = self.db['users'].find_one({'url': item['url']})
            if user:
                item['updatedAt'] = datetime.utcnow()
                updated_user = merge_dict(user, item)
                self.db['users'].update_one({'_id': user['_id']}, {'$set': updated_user})
                return user['_id']
            else:
                item['createdAt'] = datetime.utcnow()
                item['updatedAt'] = datetime.utcnow()
                return self.db['users'].insert_one(item).inserted_id
        return None

    def process_review(self, item: Review) -> [str, None]:
        """Save Review object to the database.

        :return: id of updated or created review
        :param item: Review
        """

        item = ItemAdapter(item).asdict()

        if 'parentReviewedAt' in item and 'parentReviewableType' in item and 'parentReviewableUrl' in item:
            if 'parentUserUrl' not in item:
                item['parentUserUrl'] = None
            parent_review = Review({'userUrl': item['parentUserUrl'], 'reviewedAt': item['parentReviewedAt'], 'reviewableType': item['parentReviewableType'], 'reviewableUrl': item['parentReviewableUrl']})
            item['parentId'] = self.process_review(parent_review)
            del item['parentUserUrl']
            del item['parentReviewedAt']
            del item['parentReviewableType']
            del item['parentReviewableUrl']
        else:
            item['parentId'] = None

        if 'userUrl' in item:
            # check if review user already exists
            user = self.db['users'].find_one({'url': item['userUrl']})
            if user:
                item['userId'] = user['_id']
            else:
                item['userId'] = self.process_user(User({'url': item['userUrl']}), True)
            del item['userUrl']
        else:
            # anonymous user
            item['userId'] = None

        if 'reviewableType' in item and 'reviewableUrl' in item:
            if item['reviewableType'] == 'Chapter':
                # check if chapter already exists
                chapter = self.db['chapters'].find_one({'url': item['reviewableUrl']})
                if chapter:
                    item['reviewableId'] = chapter['_id']
                else:
                    item['reviewableId'] = self.process_chapter(Chapter({'url': item['reviewableUrl']}), True)
            if item['reviewableType'] == 'Story':
                # check if story already exists
                story = self.db['stories'].find_one({'url': item['reviewableUrl']})
                if story:
                    item['reviewableId'] = story['_id']
                else:
                    item['reviewableId'] = self.process_story(Story({'url': item['reviewableUrl']}), True)
            del item['reviewableUrl']
        else:
            return None

        if 'reviewedAt' in item:
            # check if review already exists
            if item['userId']:
                review = self.db['reviews'].find_one({'userId': item['userId'], 'reviewedAt': item['reviewedAt'], 'reviewableType': item['reviewableType'], 'reviewableId': item['reviewableId']})
            else:  # anonymous user
                review = self.db['reviews'].find_one({'reviewedAt': item['reviewedAt'], 'reviewableType': item['reviewableType'], 'reviewableId': item['reviewableId']})
            if review:
                item['updatedAt'] = datetime.utcnow()
                updated_review = merge_dict(review, item)
                self.db['reviews'].update_one({'_id': review['_id']}, {'$set': updated_review})
                return review['_id']
            else:
                item['createdAt'] = datetime.utcnow()
                item['updatedAt'] = datetime.utcnow()
                return self.db['reviews'].insert_one(item).inserted_id
        else:
            return None
