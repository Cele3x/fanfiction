# -----------------------------------------------------------
# Traverse the character names list and predict their gender.
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
import re
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


def preprocess_names(names_df: DataFrame, first_names: bool = False) -> DataFrame:
    try:
        # replace umlauts because unidecode replaces e.g. ä to a
        names_df['preprocessed'] = names_df['name'].str.translate(UMLAUTS)
        # names_df['preprocessed'] = [name.translate(UMLAUTS) for name in names_df['name']]

        # decode characters; e.g. á => a
        names_df['preprocessed'] = names_df['preprocessed'].apply(unidecode)
        # names_df['preprocessed'] = [unidecode(name) for name in names_df['preprocessed']]

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
        # names_df['preprocessed'] = [list(name) for name in names_df['preprocessed']]
        names_df['preprocessed'] = names_df['preprocessed'].apply(lambda x: list(x))

        # pad names with spaces to make all names same length
        name_length = 50
        names_df['preprocessed'] = [(name + [' '] * name_length)[:name_length] for name in names_df['preprocessed']]

        # encode characters to numbers
        names_df['preprocessed'] = [[max(0.0, ord(char) - 96.0) for char in name] for name in names_df['preprocessed']]

        return names_df
    except Exception as ex:
        print(ex)


def predict_genders(prediction_model, names_df: DataFrame) -> DataFrame:
    try:
        preprocessed_names = np.asarray(names_df['preprocessed'].values.tolist())
        result = prediction_model.predict(preprocessed_names, batch_size=None, verbose='auto', max_queue_size=10, workers=1, use_multiprocessing=False).squeeze(axis=1)
        names_df['gender'] = ['M' if logit > 0.5 else 'F' for logit in result]
        names_df['probability'] = [logit if logit > 0.5 else 1.0 - logit for logit in result]
        return names_df
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
    try:
        # load serialized model with weights
        model = load_model('data/gender_classifier.json', 'data/gender_classifier.h5')

        # read names from training data
        df_names_train = pd.read_csv('data/names_binary_ascii.csv')
        df_names_train['probability'] = 1.0

        # read names from fanfiction corpus
        df_names_corpus = pd.read_csv('data/character_names.csv')

        # merge names from training data and fanfiction corpus
        df = pd.concat([df_names_train, df_names_corpus], ignore_index=True)

        # remove duplicate names
        df.drop_duplicates(subset='name', keep='first', inplace=True)

        # get names that are not yet predicted
        df_unpredicted = df[df['gender'].isnull()]

        # predict names in chunks
        chunk_size = 10000
        with tqdm(total=chunk_size) as pbar:
            for df_chunk in np.array_split(df_unpredicted, chunk_size):
                df_chunk = preprocess_names(df_chunk)
                df_chunk = predict_genders(model, df_chunk)
                df = pd.concat([df, df_chunk], ignore_index=True)
                pbar.update(1)

        # additional predictions for names that have a low probability
        # TODO: maybe filter for names containing spaces
        df_low_probability = df[df['probability'] < 0.8]

        # predict names in chunks
        chunk_size = 10000
        with tqdm(total=chunk_size) as pbar:
            for df_chunk in np.array_split(df_low_probability, chunk_size):
                df_chunk = preprocess_names(df_chunk)
                df_chunk = predict_genders(model, df_chunk)
                df = pd.concat([df, df_chunk], ignore_index=True)

        df.to_csv('data/character_names_predicted.csv', index=False)

    except Exception as e:
        print(e)
