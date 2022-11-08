# -----------------------------------------------------------
# Predicts gender for person names using previously trained
# model.
# -----------------------------------------------------------

import pandas as pd
import numpy as np
from numpy import ndarray
from pandas import DataFrame
from tqdm import tqdm
from unidecode import unidecode
from utils.db_connect import DatabaseConnection
from datetime import datetime
from pymongo import UpdateOne
import tensorflow as tf
keras = tf.keras
from keras.models import model_from_json
# from keras.models import load_model

UMLAUTS = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}


def load_model(json_model_path: str, weights_path: str):
    try:
        # load model from json file
        with open(json_model_path, 'r') as json_file:
            loaded_model_json = json_file.read()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights(weights_path)

        return loaded_model
    except Exception as ex:
        print(ex)


def preprocess_names(names_df: DataFrame) -> DataFrame:
    try:
        # replace umlauts because unidecode replaces e.g. ä to a
        names_df['name'] = [name.translate(UMLAUTS) for name in names_df['name']]

        # decode characters; e.g. á => a
        names_df['name'] = [unidecode(name) for name in names_df['name']]

        # convert name to lowercase (as done for training)
        names_df['name'] = names_df['name'].str.lower()

        # strip whitespaces
        names_df['name'] = [name.strip() for name in names_df['name']]

        # split individual characters
        names_df['name'] = [list(name) for name in names_df['name']]

        # pad names with spaces to make all names same length
        name_length = 50
        names_df['name'] = [(name + [' '] * name_length)[:name_length] for name in names_df['name']]

        # encode characters to numbers
        names_df['name'] = [[max(0.0, ord(char) - 96.0) for char in name] for name in names_df['name']]

        return names_df
    except Exception as ex:
        print(ex)


def predict_genders(prediction_model, names: ndarray) -> DataFrame:
    try:
        result = prediction_model.predict(names, verbose=0).squeeze(axis=1)
        pred_df['gender'] = ['M' if logit > 0.5 else 'F' for logit in result]
        pred_df['probability'] = [logit if logit > 0.5 else 1.0 - logit for logit in result]
        return pred_df
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load dataframe with names
        df = pd.read_csv('data/temp_names.csv')
        df['probability'] = 1.0

        # load serialized model with weights
        model = load_model('data/gender_classifier.json', 'data/gender_classifier.h5')

        with client.start_session() as session:

            # find tagged persons
            story_query = {'isTagged': True, 'isPredicted': False}
            stories = db.stories.find(story_query, session=session, no_cursor_timeout=True)
            num_stories = db.stories.count_documents(story_query)

            story_iterator = 0

            for story in stories:
                story_iterator += 1
                print('\n%s - Processing story %d of %d...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), story_iterator, num_stories))

                db_updates = []
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

                        persons = list(chapter['persons'].keys())
                        prev_df = df.loc[df['name'].isin(persons)]

                        # process only new names
                        open_persons = list(set(persons) - set(prev_df['name']))
                        if open_persons:
                            pred_df = pd.DataFrame({'name': open_persons})
                            pred_df = preprocess_names(pred_df)
                            pred_df = predict_genders(model, np.asarray(pred_df['name'].values.tolist()))
                            pred_df['name'] = open_persons

                            # process again if there are potential firstnames
                            pred_df_2 = pred_df.loc[(pred_df['probability'] <= 0.8) & (' ' in pred_df['name'])]
                            if not pred_df_2.empty:
                                open_persons = list(pred_df_2['name'])
                                first_names = [name.split(' ')[0] for name in open_persons]
                                pred_df_2 = pd.DataFrame({'name': first_names})
                                pred_df_2 = preprocess_names(pred_df_2)
                                pred_df_2 = predict_genders(model, np.asarray(pred_df_2['name'].values.tolist()))
                                pred_df_2['name'] = open_persons
                            df = pd.concat([df, pred_df, pred_df_2])
                            df_merged = pd.concat([prev_df, pred_df, pred_df_2])
                        else:
                            df_merged = prev_df
                        # df_merged.drop_duplicates(inplace=True)
                        df_merged = df_merged.drop_duplicates(subset=['name'])

                        # count occurances of persons
                        for index, row in df_merged.iterrows():
                            if row['name'] in chapter['persons']:
                                count = chapter['persons'][row['name']]
                            else:
                                continue

                            # count only with high probability
                            if row['gender'] and row['probability'] and row['probability'] > 0.8:
                                if row['gender'] == 'F':
                                    females += count
                                    story_females += count
                                elif row['gender'] == 'M':
                                    males += count
                                    story_males += count
                                else:
                                    indecisives += count
                                    story_indecisives += count
                            else:
                                indecisives += count
                                story_indecisives += count

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
                        db_updates.append(UpdateOne({'_id': chapter['_id']}, {'$set': {'personGenders': person_genders}}))
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

                # update db
                if db_updates:
                    print('%s - Updating %d chapters...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_updates)))
                    db.chapters.bulk_write(db_updates)

                db.stories.update_one({'_id': story['_id']}, {'$set': {'isPredicted': True, 'personGenders': story_person_genders}})

                if story_iterator % 100 == 0:
                    print('\n%s - Saving DataFrame to CSV...\n' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())))
                    df.to_csv('data/temp_names.csv', index=False)
                    client.refresh_session(session.session_id)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
