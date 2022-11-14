# -----------------------------------------------------------
# Traverse the character names list and predict their gender.
# -----------------------------------------------------------

import pandas as pd
import numpy as np
from pandas import DataFrame
from tqdm import tqdm
from unidecode import unidecode
from datetime import datetime
import tensorflow as tf
import traceback

# fix for apple m1
keras = tf.keras

UMLAUTS = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}


def preprocess_names(names_df: DataFrame, first_names: bool = False) -> DataFrame:
    try:
        # replace umlauts because unidecode replaces e.g. ä to a
        names_df['preprocessed'] = names_df['name'].str.translate(UMLAUTS)

        # decode characters; e.g. á => a
        names_df['preprocessed'] = names_df['preprocessed'].apply(unidecode)

        # convert name to lowercase (as done for training)
        names_df['preprocessed'] = names_df['preprocessed'].str.lower()

        # remove all non-alphabetic characters
        names_df['preprocessed'] = names_df['preprocessed'].str.replace(r'[^\w\s]', '', regex=True)

        # strip whitespaces
        names_df['preprocessed'] = names_df['preprocessed'].str.strip()

        # get first names only
        if first_names:
            names_df['preprocessed'] = names_df['preprocessed'].str.split().str[0]

        # split individual characters
        names_df['preprocessed'] = names_df['preprocessed'].apply(lambda x: list(x))

        # pad names with spaces to make all names same length
        name_length = 50
        names_df['preprocessed'] = [(name + [' '] * name_length)[:name_length] for name in names_df['preprocessed']]

        # encode characters to numbers
        names_df['preprocessed'] = [[max(0.0, ord(char) - 96.0) for char in name] for name in names_df['preprocessed']]

        return names_df
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())


def predict_genders(prediction_model, names_df: DataFrame) -> DataFrame:
    try:
        preprocessed_names = np.asarray(names_df['preprocessed'].values.tolist())
        result = prediction_model.predict(preprocessed_names, batch_size=None, verbose='auto', max_queue_size=10, workers=1, use_multiprocessing=False).squeeze(axis=1)
        names_df['gender'] = ['M' if logit > 0.5 else 'F' for logit in result]
        names_df['probability'] = [logit if logit > 0.5 else 1.0 - logit for logit in result]

        # remove preprocessed column
        names_df.drop(columns=['preprocessed'], inplace=True)

        return names_df
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())


if __name__ == '__main__':
    print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
    try:
        # load model with weights
        model = keras.models.load_model('data/gender_classifier.h5')

        # read names from training data, drop empty names and set probability to 1.0
        df_names_train = pd.read_csv('data/names.csv')
        df_names_train.dropna(subset=['name'], inplace=True)
        df_names_train['name'] = df_names_train['name'].str.lower()
        df_names_train['probability'] = 1.0

        # read names from fanfiction corpus, drop empty names and set probability to 0.0
        df_names_corpus = pd.read_csv('data/character_names.csv')
        df_names_corpus.dropna(subset=['name'], inplace=True)
        df_names_corpus['probability'] = 0.0

        # merge names from training data and fanfiction corpus
        df = pd.concat([df_names_train, df_names_corpus], ignore_index=True)

        # remove duplicate names and keep the one from the training data
        df.drop_duplicates(subset='name', keep='first', inplace=True)

        # get names that are not yet predicted
        df_unpredicted = df[df['gender'].isnull()]

        df_predicted_1 = DataFrame()
        # predict names in chunks
        sections = 100
        with tqdm(total=sections) as pbar:
            for df_chunk in np.array_split(df_unpredicted, sections):
                df_chunk = preprocess_names(df_chunk)
                df_chunk = predict_genders(model, df_chunk)
                df_predicted_1 = pd.concat([df_predicted_1, df_chunk], ignore_index=True)
                pbar.update(1)

        # additional predictions for names that have a low probability and contain spaces for potential first names
        df_low_probability = df_predicted_1[(df_predicted_1['probability'] < 0.8) & (df_predicted_1['name'].str.contains(r'\s', regex=True))]

        df_predicted_2 = DataFrame()
        # predict names in chunks
        sections = 20
        with tqdm(total=sections) as pbar:
            for df_chunk in np.array_split(df_low_probability, sections):
                df_chunk = preprocess_names(df_chunk, first_names=True)
                df_chunk = predict_genders(model, df_chunk)
                df_predicted_2 = pd.concat([df_predicted_2, df_chunk], ignore_index=True)
                pbar.update(1)

        df_predicted = pd.concat([df_names_train, df_predicted_2, df_predicted_1], ignore_index=True)

        # drop duplicate names
        df_predicted = df_predicted.drop_duplicates(subset='name', keep='first')
        df_predicted = df_predicted.dropna(subset=['name'])

        # sort by name
        df_predicted = df_predicted.sort_values(by=['name'])

        # redo the index
        df_predicted = df_predicted.reset_index(drop=True)

        # save to csv
        df_predicted.to_csv('data/character_names_predicted.csv', index=False)

    except Exception as e:
        print(e)
        print(traceback.format_exc())
