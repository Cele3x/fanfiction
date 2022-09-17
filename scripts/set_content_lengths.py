#!/usr/bin/python3

# -----------------------------------------------------------
# Traverses through all the chapters and stories counting
# sentences, words, letter characters and all characters
# while storing the results for each document.
# -----------------------------------------------------------

from bson import ObjectId
from pymongo import UpdateOne
from pymongo.database import Database
from spacy import Language
from tqdm import tqdm
import re
import spacy
from db_connect import DatabaseConnection
from multiprocessing import Pool, cpu_count, freeze_support
from math import ceil
from typing import Optional, Union


def count_chapter_items(nlp: Language, chapter_id: ObjectId, text: str) -> Union[None, UpdateOne]:
    try:
        # count sentences
        doc = nlp(text)
        sentence_tokens = [[token.text for token in sent] for sent in doc.sents]
        sentence_count = len(sentence_tokens)

        # count words
        content_words = re.sub(r'[^\w\s]+', '', text).strip()
        word_count = len(content_words.split())

        # count characters
        content_letters = re.sub(r'\W+', '', text)
        character_count = len(text)
        character_letters_count = len(content_letters)

        return UpdateOne({'_id': chapter_id}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}})
    except Exception as ex:
        print(ex)
        return None


def count_story_items(story_sum: dict) -> Union[None, UpdateOne]:
    try:
        sentence_count = 0
        word_count = 0
        character_letters_count = 0
        character_count = 0

        if story_sum:
            if 'numSentences' in story_sum:
                sentence_count = story_sum['numSentences']
            if 'numWords' in story_sum:
                word_count = story_sum['numWords']
            if 'numLetters' in story_sum:
                character_letters_count = story_sum['numLetters']
            if 'numCharacters' in story_sum:
                character_count = story_sum['numCharacters']
            return UpdateOne({'_id': story_sum['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}})
        return None
    except Exception as ex:
        print(ex)
        return None


def process_chapters(db: Database, process_count: int = None) -> bool:
    try:
        nlp = spacy.load('de_core_news_sm')

        print('Number of CPUs: %i' % cpu_count())
        process_count = process_count or cpu_count()

        print('Using %i processes for processing chapters.' % process_count)

        chapter_count = db.chapters.count_documents({'numSentences': None})
        print('Chapters: %i' % chapter_count)

        batchsize = 1000
        for i in range(0, chapter_count, batchsize):
            chapters = db.chapters.find({'numSentences': None}).limit(batchsize)
            chapter_tuples = [(nlp, chapter['_id'], chapter['content']) for chapter in chapters]
            status_desc = 'Batch %i/%i' % (i / batchsize + 1, ceil(chapter_count / batchsize))

            with Pool(process_count) as mp_pool:
                result = mp_pool.starmap_async(count_chapter_items, tqdm(chapter_tuples, total=len(chapter_tuples), desc=status_desc), chunksize=20)
                result.wait()
                results_filtered = list(filter(None, result.get()))
                if results_filtered:
                    db.chapters.bulk_write(results_filtered)

        return True
    except Exception as ex:
        print(ex)
        return False


def process_stories(db: Database, process_count: int = None) -> bool:
    try:
        print('Number of CPUs: %i' % cpu_count())
        process_count = process_count or cpu_count()

        print('Using %i processes for processing stories.' % process_count)
        stories_count = db.stories.count_documents({'$or': [{'numSentences': None}, {'numSentences': 0}]})
        print('Stories: %i' % stories_count)

        batchsize = 10000
        for i in range(0, stories_count, batchsize):
            stories = db.stories.find({'$or': [{'numSentences': None}, {'numSentences': 0}]}).limit(batchsize)
            story_ids = [story['_id'] for story in stories]
            pipeline = [
                {'$match': {'storyId': {'$in': story_ids}, 'numSentences': {'$exists': True}}},
                {'$group': {'_id': '$storyId', 'numSentences': {'$sum': '$numSentences'}, 'numWords': {'$sum': '$numWords'}, 'numLetters': {'$sum': '$numLetters'}, 'numCharacters': {'$sum': '$numCharacters'}}}
            ]
            story_nums = list(db.chapters.aggregate(pipeline))
            status_desc = 'Batch %i/%i' % (i / batchsize + 1, ceil(stories_count / batchsize))

            with Pool(process_count) as mp_pool:
                result = mp_pool.map_async(count_story_items, tqdm(story_nums, total=len(story_nums), desc=status_desc), chunksize=20)
                result.wait()
                results_filtered = list(filter(None, result.get()))
                if results_filtered:
                    db.stories.bulk_write(results_filtered)

        return True
    except Exception as ex:
        print(ex)
        return False


if __name__ == "__main__":
    freeze_support()
    client = DatabaseConnection()
    try:
        database = client.connect('FanFiction')
        if database is None:
            raise Exception('Database connection failed.')

        if process_chapters(database):
            print('Processing chapters done!')
        if process_stories(database):
            print('Processing stories done!')

    except Exception as e:
        print(e)
    finally:
        client.disconnect()
