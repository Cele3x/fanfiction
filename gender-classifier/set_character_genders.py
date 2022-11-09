# -----------------------------------------------------------
# Sets and counts gender occurances for stories using the
# previously predicted names list.
# -----------------------------------------------------------

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
        df = pd.read_csv('data/character_names_predicted.csv', usecols=['name', 'gender', 'probability'], dtype={'name': str, 'gender': str, 'probability': float})

        with client.start_session() as session:

            # find tagged persons
            story_query = {'isTagged': True, 'isPredicted': False}
            stories = db.stories.find(story_query, session=session, no_cursor_timeout=True).sort('_id', pymongo.DESCENDING)
            num_stories = db.stories.count_documents(story_query)

            # initialize update containers
            db_chapter_updates = []
            db_story_updates = []

            for index, story in enumerate(stories):
                print('\n%s - Processing story %d of %d...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), index + 1, num_stories))

                # initialize counters
                story_females = 0
                story_males = 0
                story_indecisives = 0

                # find tagged chapters
                chapter_query = {'storyId': story['_id'], 'isTagged': True}
                chapters = db.chapters.find(chapter_query, session=session, no_cursor_timeout=True)
                num_chapters = db.chapters.count_documents(chapter_query)

                with tqdm(total=num_chapters) as pbar:
                    for chapter in chapters:
                        pbar.set_description('Processing chapter %s...' % (chapter['_id']))
                        females = 0
                        males = 0
                        indecisives = 0

                        for name, occurrences in chapter['persons'].items():
                            # find name in dataframe
                            if name not in df.index:
                                print('Name "%s" not found in dataframe.' % name)
                                continue

                            # get row
                            row = df.loc[name]

                            # count only with high probability
                            if row['gender'] and row['probability'] and row['probability'] > 0.8:
                                if row['gender'] == 'F':
                                    females += occurrences
                                    story_females += occurrences
                                elif row['gender'] == 'M':
                                    males += occurrences
                                    story_males += occurrences
                                else:
                                    indecisives += occurrences
                                    story_indecisives += occurrences
                            else:
                                indecisives += occurrences
                                story_indecisives += occurrences

                            # print('Name: %s [%s, %0.2f%%]' % (person, gender, probability))

                        # count all predictions with high probability
                        total_decisives = females + males

                        # count all predictions
                        total = total_decisives + indecisives

                        decisive_percentage = 0.0 if total_decisives == 0 else round(total_decisives / (total_decisives + indecisives), 2)
                        female_percentage = 0.0 if total_decisives == 0 else round(females / total, 2)
                        male_percentage = 0.0 if total_decisives == 0 else round(males / total, 2)
                        ratio = float(females) if males == 0 else round(females / males, 2)

                        # result object with counts of occurances, female/male ratio and percentages
                        person_genders = {'females': females, 'males': males, 'indecisives': indecisives, 'ratio': ratio,
                                          'decisivePct': decisive_percentage, 'femalePct': female_percentage, 'malePct': male_percentage}

                        # if db.chapters.update_one({'_id': chapter['_id']}, {'$set': {'personGenders': person_genders}}):
                        # print('Updated %s with personGender: %s' % (chapter['_id'], person_genders))
                        db_chapter_updates.append(UpdateOne({'_id': chapter['_id']}, {'$set': {'personGenders': person_genders}}))
                        pbar.update(1)

                # calculate story statistics
                story_total_decisives = story_females + story_males
                story_total = story_total_decisives + story_indecisives
                story_decisive_percentage = 0.0 if story_total_decisives == 0 else round(story_total_decisives / (story_total_decisives + story_indecisives), 2)
                story_female_percentage = 0.0 if story_total_decisives == 0 else round(story_females / story_total, 2)
                story_male_percentage = 0.0 if story_total_decisives == 0 else round(story_males / story_total, 2)
                story_ratio = float(story_females) if story_males == 0 else round(story_females / story_males, 2)
                story_person_genders = {'females': story_females, 'males': story_males, 'indecisives': story_indecisives, 'ratio': story_ratio,
                                        'decisivePct': story_decisive_percentage, 'femalePct': story_female_percentage, 'malePct': story_male_percentage}

                db_story_updates.append(UpdateOne({'_id': story['_id']}, {'$set': {'isPredicted': True, 'personGenders': story_person_genders}}))

                # refresh every 5000 stories the session
                if index % 5000 == 0:
                    client.refresh_session(session.session_id)

                    # bulk write chapter updates
                    if db_chapter_updates:
                        print('%s - Updating %d chapters...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_chapter_updates)))
                        db.chapters.bulk_write(db_chapter_updates)
                        db_chapter_updates = []

                    # bulk write story updates
                    if db_story_updates:
                        print('%s - Updating %d stories...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_story_updates)))
                        db.stories.bulk_write(db_story_updates)
                        db_story_updates = []
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
