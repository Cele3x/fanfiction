#!/usr/bin/python3

# -----------------------------------------------------------
# Traverses through all the chapters and stories counting
# sentences, words, letter characters and all characters
# while storing the results for each document.
# -----------------------------------------------------------

from bson import ObjectId
from pymongo import UpdateOne
from tqdm import tqdm
import re
import spacy
from db_connect import DatabaseConnection
import multiprocessing


class LengthCalculator:

    def __init__(self):
        self.client = DatabaseConnection()
        self.db = self.client.connect('FanFiction')
        self.nlp = spacy.load('de_core_news_sm')
        self.chapter_updates = []
        self.story_updates = []

    def perform(self):
        try:
            if self.process_chapters():
                print('Processed chapters!')
            if self.process_stories():
                print('Processed stories!')
        except Exception as e:
            print(e)
        finally:
            self.client.disconnect()

    def count_items(self, chapter_id: ObjectId, text: str) -> None:
        # count sentences
        doc = self.nlp(text)
        sentence_tokens = [[token.text for token in sent] for sent in doc.sents]
        sentence_count = len(sentence_tokens)

        # count words
        content_words = re.sub(r'[^\w\s]+', '', text).strip()
        word_count = len(content_words.split())

        # count characters
        content_letters = re.sub(r'\W+', '', text)
        character_count = len(text)
        character_letters_count = len(content_letters)

        self.chapter_updates.append(UpdateOne({'_id': chapter_id}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}}))

    def process_chapters(self) -> bool:
        try:
            chapters = self.db.chapters.find({'numSentences': None})
            chapter_count = self.db.chapters.count_documents({'numSentences': None})

            processes = []
            with tqdm(total=chapter_count) as pbar_chapter:
                for index, chapter in enumerate(chapters):
                    pbar_chapter.set_description('Processing chapter %s' % chapter['_id'])

                    if 'content' in chapter and isinstance(chapter['content'], str):
                        p = multiprocessing.Process(target=self.count_items, args=(chapter['_id'], chapter['content']))
                        processes.append(p)
                        p.start()

                    if index > 1000:
                        pbar_chapter.set_description('Writing bulk data with %s items' % len(self.chapter_updates))
                        self.db.chapters.bulk_write(self.chapter_updates)
                        self.chapter_updates = []

                    pbar_chapter.update(1)

            pbar_chapter.set_description('Writing bulk data with %s items' % len(self.chapter_updates))
            self.db.chapters.bulk_write(self.chapter_updates)
            return True
        except Exception as e:
            print(e)
            return False

    def process_stories(self) -> bool:
        try:
            stories_count = self.db.stories.count_documents({'numSentences': None})
            stories = self.db.stories.find({'numSentences': None})

            with tqdm(total=stories_count) as pbar_story:
                for index, story in enumerate(stories):
                    pbar_story.set_description('Processing story %s' % story['_id'])

                    sentence_count = 0
                    word_count = 0
                    character_letters_count = 0
                    character_count = 0

                    story_sums = self.db.chapters.aggregate([
                        {'$match': {'storyId': story['_id'], 'numSentences': {'$exists': True}}},
                        {'$group': {
                            '_id': '$storyId',
                            'numSentences': {'$sum': '$numSentences'},
                            'numWords': {'$sum': '$numWords'},
                            'numLetters': {'$sum': '$numLetters'},
                            'numCharacters': {'$sum': '$numCharacters'}}}
                    ])

                    if 'numSentences' in story_sums:
                        sentence_count = story_sums['numSentences']
                    if 'numWords' in story_sums:
                        word_count = story_sums['numWords']
                    if 'numLetters' in story_sums:
                        character_letters_count = story_sums['numLetters']
                    if 'numCharacters' in story_sums:
                        character_count = story_sums['numCharacters']

                    self.story_updates.append(UpdateOne({'_id': story['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}}))

                    if index > 1000:
                        pbar_story.set_description('Writing bulk data with %s items' % len(self.story_updates))
                        self.db.stories.bulk_write(self.story_updates)
                        self.story_updates = []

                    pbar_story.update(1)

                pbar_story.set_description('Writing bulk data with %s items' % len(self.story_updates))
                self.db.stories.bulk_write(self.story_updates)
                return True
        except Exception as e:
            print(e)
            return False
