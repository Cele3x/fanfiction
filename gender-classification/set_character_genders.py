# -----------------------------------------------------------
# Sets and counts gender occurances for stories using the
# previously predicted names list.
# -----------------------------------------------------------
import time

import pandas as pd
import pymongo
from tqdm import tqdm
from utils.db_connect import DatabaseConnection
from datetime import datetime
from pymongo import UpdateOne
import timeit


if __name__ == '__main__':
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load dataframe with names
        df = pd.read_csv('data/character_names_predicted.csv', usecols=['name', 'gender', 'probability'], dtype={'name': str, 'gender': str, 'probability': float}, index_col=0)

        with client.start_session() as session:

            # find tagged persons
            story_query = {'isPredicted': False, 'persons': {'$exists': True}}
            stories = db.stories.find(story_query, {'_id': 1, 'persons': 1}, session=session, no_cursor_timeout=True)
            story_count = db.stories.count_documents(story_query)

            # initialize story update container
            db_story_updates = []
            missing_names = set()

            with tqdm(total=story_count, position=0, leave=False, colour='#71B1D9') as pbar:
                for index, story in enumerate(stories):
                    pbar.set_description('Processing story %s...' % (story['_id']))

                    # initialize counters
                    females = 0
                    males = 0
                    indecisives = 0

                    # iterate over persons
                    with tqdm(total=len(story['persons']), position=1, leave=False, colour='#AED8F2') as pbar_person:
                        for name, occurrences in story['persons'].items():
                            pbar_person.set_description('Processing person %s...' % name)

                            # find name in dataframe
                            if name not in df.index:
                                pbar.set_description('Name "%s" not found in dataframe [%s]' % (name, story['_id']))
                                missing_names.add(name)
                                continue

                            # get row
                            row = df.loc[name]

                            # count only with high probability
                            if row['gender'] and row['probability'] and row['probability'] > 0.8:
                                if row['gender'] == 'F':
                                    females += occurrences
                                elif row['gender'] == 'M':
                                    males += occurrences
                                else:
                                    indecisives += occurrences
                            else:
                                indecisives += occurrences

                            pbar_person.update(1)

                    # calculate story statistics
                    decisives = females + males
                    total = decisives + indecisives
                    decisive_percentage = 0.0 if decisives == 0 else round(decisives / total, 2)
                    female_percentage = 0.0 if decisives == 0 else round(females / total, 2)
                    male_percentage = 0.0 if decisives == 0 else round(males / total, 2)
                    ratio = 0.5 if decisives == 0 else round(males / decisives, 2)
                    person_genders = {'females': females, 'males': males, 'indecisives': indecisives, 'ratio': float(ratio),
                                      'decisivePct': float(decisive_percentage), 'femalePct': float(female_percentage), 'malePct': float(male_percentage)}

                    db_story_updates.append(UpdateOne({'_id': story['_id']}, {'$set': {'isPredicted': True, 'genders': person_genders}}))

                    # refresh every 5000 stories the session and update the database
                    if (index + 1) % 5000 == 0:
                        client.refresh_session(session.session_id)

                        # bulk write story updates
                        if db_story_updates:
                            pbar.set_description('Updating %d stories...' % len(db_story_updates))
                            db.stories.bulk_write(db_story_updates)
                            db_story_updates = []

                    pbar.update(1)

            print('%s - Updating %d stories...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_story_updates)))
            db.stories.bulk_write(db_story_updates)

            if missing_names:
                print('Missing names:', ', '.join(missing_names))
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
