# -----------------------------------------------------------
# Predicts gender for person names using previously trained
# model.
# -----------------------------------------------------------

import tensorflow as tf
from unidecode import unidecode

keras = tf.keras
from keras.models import model_from_json
from scripts.db_connect import DatabaseConnection
from datetime import datetime

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


def preprocess_name(name: str) -> list:
    try:
        # replace umlauts because unidecode replaces e.g. ä to a
        name = name.translate(UMLAUTS)

        # decode characters; e.g. á => a
        name = unidecode(name)

        # convert name to lowercase (as done for training)
        name = name.lower().strip()

        # split individual characters
        name = list(name)

        # pad names with spaces to make all names same length
        name_length = 50
        name = (name + [' '] * name_length)[:name_length]

        # encode characters to numbers
        name = [max(0.0, ord(char) - 96.0) for char in name]

        return name
    except Exception as ex:
        print(ex)


def predict_gender(prediction_model, name: list):
    try:
        result = prediction_model.predict([name]).squeeze(axis=1)
        predicted_gender = ['Male' if logit > 0.5 else 'Female' for logit in result][0]
        predicted_probability = [logit if logit > 0.5 else 1.0 - logit for logit in result][0]
        return predicted_gender, predicted_probability
    except Exception as ex:
        print(ex)
        return None, None


if __name__ == '__main__':
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load serialized model with weights
        model = load_model('data/gender_classifier.json', 'data/gender_classifier.h5')

        # find chapters tagged with flair NLP
        chapters = db.chapters.find({'isTagged': True, 'persons': {'$exists': True}})

        # store previously predicted genders
        predicted_persons = {}

        for chapter in chapters:
            females = 0
            males = 0
            indecisives = 0

            # structure {<NAME-1>: <OCCURANCES-NAME-1>, <NAME-2>: <OCCURANCES-NAME-2>, ...}
            for n in chapter['persons'].keys():
                if n in predicted_persons:  # use previously predicted value if available
                    gender, probability = predicted_persons[n]
                else:
                    preprocessed_name = preprocess_name(n)
                    gender, probability = predict_gender(model, preprocessed_name)
                    predicted_persons[n] = [gender, probability]

                # count only with high probability
                if gender and probability and probability > 0.8:
                    if gender == 'Female':
                        females += 1
                    elif gender == 'Male':
                        males += 1
                    else:
                        indecisives += 1
                else:
                    indecisives += 1

                print('Name: %s [%s, %0.2f%%]' % (n, gender, probability))

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

            if db.chapters.update_one({'_id': chapter['_id']}, {'$set': {'personGenders': person_genders}}):
                print('Updated %s with personGender: %s' % (chapter['_id'], person_genders))
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
