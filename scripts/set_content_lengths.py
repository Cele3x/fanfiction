#!/usr/bin/python3
from typing import Optional, Union

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
        story_ids = [ObjectId("62df62894cbb9245c00df0a5"), ObjectId("62e0542ee4dc1fde8b9fa822"), ObjectId("62e0542ee4dc1fde8b9fa822"), ObjectId("62e0542ee4dc1fde8b9fa822"), ObjectId("62e0542ee4dc1fde8b9fa822"), ObjectId("62e0542ee4dc1fde8b9fa822"), ObjectId("62e0a966e4dc1fde8b9fc24c"), ObjectId("62e14cac1352b1d6c3d4c35b"), ObjectId("62e154721352b1d6c3d4d3b4"), ObjectId("62e198b71338c6207ba89db4"), ObjectId("62e19b0c1338c6207ba8a3c3"), ObjectId("62e19b0c1338c6207ba8a3c3"), ObjectId("62e19b0c1338c6207ba8a3c3"), ObjectId("62e1a2d41338c6207ba8b1d4"), ObjectId("62e1a2d41338c6207ba8b1d4"), ObjectId("62e1a4db1338c6207ba8b668"), ObjectId("62e1a6031338c6207ba8b8d5"), ObjectId("62e1ce821338c6207ba8cb55"), ObjectId("62e234321338c6207ba8dca3"), ObjectId("62e235c41338c6207ba8e1b3"), ObjectId("62e236ee1338c6207ba8e58e"), ObjectId("62e237f31338c6207ba8e7f4"), ObjectId("62e23b001338c6207ba8f1f8"), ObjectId("62e23dc01338c6207ba8f9f3"), ObjectId("62e23dc01338c6207ba8f9f3"), ObjectId("62e23ee21338c6207ba8fc75"), ObjectId("62e23ee21338c6207ba8fc75"), ObjectId("62e2405c1338c6207ba9011a"), ObjectId("62e246b41338c6207ba91066"), ObjectId("62e246d61338c6207ba910a2"), ObjectId("62e24b281338c6207ba919ea"), ObjectId("62e278e51338c6207ba96e2e"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27b561338c6207ba973cc"), ObjectId("62e27c681338c6207ba97787"), ObjectId("62e27c681338c6207ba97787"), ObjectId("62e27c681338c6207ba97787"), ObjectId("62e27f181338c6207ba97e62"), ObjectId("62e27f181338c6207ba97e62"), ObjectId("62e27f181338c6207ba97e62"), ObjectId("62e281b21338c6207ba98689"), ObjectId("62e4c50266e522efe03aefaa"), ObjectId("62e4c50266e522efe03aefaa"), ObjectId("62e4df6a66e522efe03b0a69"), ObjectId("62e52086b4a7f454e92fc4a2"), ObjectId("62e538d8b4a7f454e92fe449"), ObjectId("62e56a21b4a7f454e93004e4"), ObjectId("62e56a98b4a7f454e93005ef"), ObjectId("62e577deb4a7f454e9301fb0"), ObjectId("62e577deb4a7f454e9301fb0"), ObjectId("62e57845b4a7f454e9302039"), ObjectId("62e57845b4a7f454e9302039"), ObjectId("62e57845b4a7f454e9302039"), ObjectId("62e57845b4a7f454e9302039"), ObjectId("62e58310b4a7f454e9302486"), ObjectId("62e5831ab4a7f454e9302498"), ObjectId("62e5b085b4a7f454e93047c5"), ObjectId("62e6832b0ab843d3ca7f0c58"), ObjectId("62e6897a0ab843d3ca7f15bf"), ObjectId("62e68bf40ab843d3ca7f1772"), ObjectId("62e68c4a0ab843d3ca7f181d"), ObjectId("62e6fc65d44a94f9dc90148a"), ObjectId("62e72a46d44a94f9dc9023de"), ObjectId("62e8a625d0c5832fcf3c734f"), ObjectId("62eb318c6df3ba17bf342362"), ObjectId("62eba7816df3ba17bf344c5f"), ObjectId("62ebd9e39107bc230d06c2c5"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ebef329107bc230d06df36"), ObjectId("62ec02559107bc230d06eb48"), ObjectId("62ed593d250d2fdb4a51676b"), ObjectId("62ed5f04250d2fdb4a517381"), ObjectId("62ed81b5250d2fdb4a51c156"), ObjectId("62ed9248250d2fdb4a51e534"), ObjectId("62ed9248250d2fdb4a51e534"), ObjectId("62ed9248250d2fdb4a51e534"), ObjectId("62ed9292250d2fdb4a51e5f5"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62ed9fac250d2fdb4a51fdbb"), ObjectId("62eda255250d2fdb4a5202e5"), ObjectId("62edaee9250d2fdb4a521874"), ObjectId("62edb12d250d2fdb4a521ce9"), ObjectId("62edc052250d2fdb4a5239cc"), ObjectId("62edd222250d2fdb4a5263fd"), ObjectId("62edf1d2250d2fdb4a529d2c"), ObjectId("62ee3c6f250d2fdb4a52d5d5"), ObjectId("62ee6874250d2fdb4a530716"), ObjectId("62ee6874250d2fdb4a530716"), ObjectId("62ee6874250d2fdb4a530716"), ObjectId("62ee6874250d2fdb4a530716"), ObjectId("62ee6874250d2fdb4a530716"), ObjectId("62ee91f7250d2fdb4a5319df"), ObjectId("62eeccde250d2fdb4a5339ab"), ObjectId("62eeccee250d2fdb4a5339c7"), ObjectId("62eeec01250d2fdb4a534bcd"), ObjectId("62f05b9d2305c4be8e242b57"), ObjectId("62f05b9d2305c4be8e242b57"), ObjectId("62f0ba1e2305c4be8e2455e6"), ObjectId("62064e68ee6de93678bd69bf"), ObjectId("62064e68ee6de93678bd69bf"), ObjectId("62064e68ee6de93678bd69bf"), ObjectId("62064e68ee6de93678bd69bf"), ObjectId("6270ebc688b86a87b24f184f"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("62007f0f0a47641efa72b0e1"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("61fa68af8048ba62aec8dfca"), ObjectId("62850e49dd0343d1ac102edc"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6270e74e88b86a87b24bd886"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6270e94e88b86a87b24dec6a"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6270e53788b86a87b2499381"), ObjectId("6288a262dd0343d1ac2bf976"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("62870e05dd0343d1ac1e7381"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("626fa9fb7ab75d83034c2c1e"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("61fa68af8048ba62aec8dfca"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("620873c9404f66d9bdae2060"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6270e5f188b86a87b24a5c48"), ObjectId("6270e94588b86a87b24de729"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("62856a34dd0343d1ac12cc18"), ObjectId("6287cd1add0343d1ac24c767"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("6270e68a88b86a87b24b0525"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("62856ecedd0343d1ac12e9cd"), ObjectId("62882a23dd0343d1ac28337d"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("627d67cbdd0343d1ace4f44f"), ObjectId("627d6a15dd0343d1ace50516"), ObjectId("6287136add0343d1ac1ea55c"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6270e97e88b86a87b24e027c"), ObjectId("6288a262dd0343d1ac2bf976"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("620b3e8bde5483694cf3ff83"), ObjectId("61fa66468048ba62aec8da01"), ObjectId("6270e7d788b86a87b24c7679"), ObjectId("62861530dd0343d1ac170192"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("626f9ad27ab75d83033e45db"), ObjectId("62856a34dd0343d1ac12cc18"), ObjectId("6204cf7cee6de93678b89ef4"), ObjectId("6207a56dee6de93678c19adb"), ObjectId("62879ac6dd0343d1ac22c823"), ObjectId("6288a262dd0343d1ac2bf976"), ObjectId("6288a262dd0343d1ac2bf976"), ObjectId("61fa68af8048ba62aec8dfca"), ObjectId("620176ac775d932971a9e663"), ObjectId("6270e61b88b86a87b24a8a44"), ObjectId("61fa75268048ba62aec8fc0e"), ObjectId("6270ea9f88b86a87b24e74e5"), ObjectId("6204ad5dee6de93678b83867"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6270e94388b86a87b24de626"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("62856a34dd0343d1ac12cc18"), ObjectId("6285d624dd0343d1ac15a267"), ObjectId("6288380edd0343d1ac28c3f3"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("620601b3ee6de93678bc8a23"), ObjectId("626fa9407ab75d83034b7beb"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6270e8ad88b86a87b24d5e2c"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6270e4b588b86a87b2490e66"), ObjectId("6270ea5088b86a87b24e4b52"), ObjectId("6270e83c88b86a87b24ce50d"), ObjectId("61fb1b91f6722748dc2065e8"), ObjectId("620078900a47641efa72a07d"), ObjectId("627a54e2db27d10e00d699a2"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6270e87388b86a87b24d222b"), ObjectId("6288b579dd0343d1ac2c7dd4"), ObjectId("6204afabee6de93678b83ed9"), ObjectId("62056ba6ee6de93678ba8ac4"), ObjectId("61fa68af8048ba62aec8dfca"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("620f0a8ede5483694cfb9353"), ObjectId("620359f9775d932971aeb511"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("6270e53588b86a87b249925a"), ObjectId("62854219dd0343d1ac118a05"), ObjectId("6287a74ddd0343d1ac23318c"), ObjectId("62043d8aee6de93678b6f6bd"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("6200f3f10a47641efa740ec4"), ObjectId("626fa6cd7ab75d830349277f"), ObjectId("6270e94388b86a87b24de626"), ObjectId("6270e53788b86a87b2499381"), ObjectId("6207a582ee6de93678c19b07"), ObjectId("6270e52b88b86a87b249879d"), ObjectId("62878d49dd0343d1ac22507d"), ObjectId("6287cd32dd0343d1ac24c83b"), ObjectId("6288b579dd0343d1ac2c7dd4"), ObjectId("6207a582ee6de93678c19b07")]
        stories_count = db.stories.count_documents({'$or': [{'numSentences': None}, {'numSentences': 0}, {'_id': {'$in': story_ids}}]})
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
