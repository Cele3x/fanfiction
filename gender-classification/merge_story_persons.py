# -----------------------------------------------------------
# Merges all persons from chapters into the story document.
# Person names get cleansed in the process.
# -----------------------------------------------------------

import re
import time
from datetime import datetime
import fnmatch
import traceback

import pandas as pd
import pymongo
from pymongo import UpdateOne
from tqdm import tqdm
from unidecode import unidecode
from collections import Counter
from utils.db_connect import DatabaseConnection

UMLAUTS = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}


def cleanse_person(person: str) -> str:
    try:
        # lowercase name
        cleansed = person.lower()

        # shortened names are valid (e.g. "H." instead of "Harry")
        if len(cleansed) == 2 and person[1] == '.':
            return cleansed

        # remove title
        cleansed = re.sub(r'dr\.', '', cleansed)

        # remove all non-alphanumeric characters except dashes
        cleansed = re.sub(r'[^\w-]', '', cleansed)
        cleansed = re.sub(r'\d', '', cleansed)

        # remove all leading and trailing whitespace and return if less than 2 characters
        cleansed = cleansed.strip()
        if len(cleansed) < 2:
            return ''

        # asciify name
        cleansed_ascii = cleansed.translate(UMLAUTS)
        cleansed_ascii = unidecode(cleansed_ascii)

        # search for ascii person in names
        if cleansed_ascii in names.index:
            return cleansed

        # search for ascii person in names without an "s" at the end if present
        if len(cleansed_ascii) > 2 and cleansed_ascii.endswith('s') and cleansed_ascii[:-1] in names.index:
            return cleansed[:-1]

        # if name part is a german word, do not use it
        if german_words_regex.match(cleansed):
            return ''

        return cleansed
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())
        return ''


def cleanse_persons() -> dict:
    try:
        cleansed = {}

        for person, occurrences in persons.items():

            # split person name into parts and cleanse each part
            parts = person.split()

            cleansed_parts = []
            for part in parts:
                # print(part, end=' ', flush=True)
                cleansed_part = cleanse_person(part)
                # print('->', cleansed_part)
                cleansed_parts.append(cleansed_part)

            # join cleansed parts
            cleansed_person = ' '.join(cleansed_parts).strip()

            # skip empty person names
            if not cleansed_person:
                continue

            # add or cumulate occurrences
            if cleansed_person in cleansed:
                cleansed[cleansed_person] += occurrences
            else:
                cleansed[cleansed_person] = occurrences

        # go over each person again and check if there is a name without the genitive ending
        for person, occurrences in cleansed.copy().items():
            if person.endswith('s') and person[:-1] in cleansed:
                cleansed[person[:-1]] += occurrences
                del cleansed[person]

        return cleansed
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())


if __name__ == '__main__':
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        names = pd.read_csv('data/names.csv', usecols=['name'], dtype={'name': str}, index_col=0)
        names = names.dropna()
        german_words = pd.read_csv('data/words.csv', usecols=['word'], dtype={'word': str}, index_col=0)
        german_words = german_words.dropna()

        german_words_regex = re.compile('|'.join(fnmatch.translate(pattern) for pattern in german_words.index if pattern))

        with client.start_session() as session:

            # find all stories
            stories = db.stories.find({'isTagged': True}, {'_id': 1}, session=session, no_cursor_timeout=True)
            story_count = db.stories.count_documents({'isTagged': True})

            # initialize story update container
            story_updates = []

            with tqdm(total=story_count, colour='#71B1D9') as story_pbar:
                for story_index, story in enumerate(stories):
                    story_pbar.set_description('Processing story %s...' % (story['_id']))

                    # find all chapters of the story
                    chapters = db.chapters.find({'storyId': story['_id'], 'persons': {'$exists': True}}, {'_id': 0, 'persons': 1}, session=session, no_cursor_timeout=True)

                    # get all persons from all chapters with their occurrences
                    persons = dict(sum((Counter(dict(chapter['persons'])) for chapter in chapters), Counter()))

                    # cleanse person names
                    cleansed_persons = cleanse_persons()

                    story_updates.append(UpdateOne({'_id': story['_id']}, {'$set': {'persons': cleansed_persons}}))

                    # update story every 5000 stories
                    if (story_index + 1) % 5000 == 0:
                        story_pbar.set_description('Saving %i updates' % len(story_updates))
                        db.stories.bulk_write(story_updates, ordered=False, session=session)
                        story_updates = []

                    story_pbar.update(1)

                story_pbar.set_description('Saving %i updates' % len(story_updates))
                db.stories.bulk_write(story_updates, ordered=False, session=session)

    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        client.disconnect()
