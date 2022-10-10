# -----------------------------------------------------------
# Persons extracted by spaCy frequently contain verbs and
# other incorrect text parts. This script removes these.
# -----------------------------------------------------------

import fnmatch
from typing import Optional

from scripts.db_connect import DatabaseConnection
from datetime import datetime
import re
from unidecode import unidecode
from pymongo import DESCENDING
import pandas as pd
from tqdm import tqdm
from pymongo import UpdateOne
from math import ceil
from multiprocessing import Pool, cpu_count, freeze_support


def remove_lowercase_words(value: str) -> str:
    try:
        parts = value.split(' ')
        res = []
        for part in parts:
            part = part.strip()
            if re.match('^[A-ZÄÖÜ]', part):
                res.append(part)
        return ' '.join(res)
    except Exception as e:
        print(e)
        return value


def cleanse_word(original: str) -> str:
    try:
        # replace all punctuations and quotes
        value = re.sub(r'[.,/#!$%^&*;:{}=\-_´`"„“\'«»‘’”~()]', ' ', original)
        value = re.sub(r'\s{2,}', ' ', value)

        # replace umlauts because unidecode replaces e.g. ä to a
        umlauts = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}
        value = value.translate(umlauts)

        # decode characters; e.g. á => a
        value = unidecode(value).strip()

        # return unless it is a valid word containing only letters, numbers and spaces
        if re.search(r'[^\w\s]', value):
            value = original.strip()

        return value
    except Exception as e:
        print(e)
        return original


def remove_german_words(value: str, words: []) -> Optional[str]:
    try:
        value_words = value.split(' ')
        parts = [value_word for value_word in value_words if not fnmatch.filter(words, value_word.lower()) and value_word.lower() + '*' not in words]
        new_word = ' '.join(parts).strip()

        return new_word
    except Exception as e:
        print(e)
        return value


def process_persons(chapter: {}, words: []) -> Optional[UpdateOne]:
    try:
        if 'persons_spacy' not in chapter:
            return None

        cleansed_persons_spacy = {}
        for person in chapter['persons_spacy'].keys():
            # print(person, end=' > ')
            cleansed_invalids = cleanse_word(person)
            cleansed_lowercase = remove_lowercase_words(cleansed_invalids)
            cleansed_words = remove_german_words(cleansed_lowercase, words)
            if cleansed_words != '':
                cleansed_persons_spacy[cleansed_words] = chapter['persons_spacy'][person]
            # print(cleansed_words)

        if cleansed_persons_spacy:
            return UpdateOne({'_id': chapter['_id']}, {'$set': {'personsSpacyClean': cleansed_persons_spacy}})
        return None
    except Exception as e:
        print(e)


if __name__ == "__main__":
    freeze_support()
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        print('Number of CPUs: %i' % cpu_count())
        process_count = cpu_count()

        data = pd.read_csv(r'../token-classifier/data/words_without_names_ascii.csv')
        df = pd.DataFrame(data, columns=['word'])
        german_words = set(df['word'])

        chapter_count = db.chapters.count_documents({'isTagged': False})

        batchsize = 10000
        for i in range(0, chapter_count, batchsize):
            chapters = db.chapters.find({'isTagged': False}).sort([('numSentences', DESCENDING)]).limit(batchsize)
            chapter_tuples = [(chapter, german_words) for chapter in chapters]
            status_desc = 'Batch %i/%i' % (i / batchsize + 1, ceil(chapter_count / batchsize))

            with Pool(process_count) as mp_pool:
                result = mp_pool.starmap_async(process_persons, tqdm(chapter_tuples, total=len(chapter_tuples), desc=status_desc), chunksize=20)
                result.wait()
                results_filtered = list(filter(None, result.get()))
                if results_filtered:
                    print(results_filtered)
                    db.chapters.bulk_write(results_filtered)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
