# -----------------------------------------------------------
# Train gender classifier model.
# -----------------------------------------------------------

import tensorflow as tf
from unidecode import unidecode

keras = tf.keras
import pandas as pd
from keras import Sequential
from keras.layers import Embedding, Bidirectional, LSTM, Dense
from keras.optimizers import Adam
import numpy as np
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
from datetime import datetime

UMLAUTS = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}


def save_model_history():
    try:
        # convert the history.history dict to a pandas DataFrame:
        hist_df = pd.DataFrame(history.history)

        # save to csv
        hist_csv_file = 'data/history_v3.csv'
        with open(hist_csv_file, mode='w') as f:
            hist_df.to_csv(f)
    except Exception as e:
        print(e)


def get_lstm_model(num_alphabets=27, name_length=50, embedding_dim=256):
    m = Sequential([
        Embedding(num_alphabets, embedding_dim, input_length=name_length),
        Bidirectional(LSTM(units=128, recurrent_dropout=0.2, dropout=0.2)),
        Dense(1, activation="sigmoid")
    ])

    m.compile(loss='binary_crossentropy',
              optimizer=Adam(learning_rate=0.001),
              metrics=['accuracy'])

    return m


def preprocess(names_df, train=True):
    # replace umlauts because unidecode replaces e.g. ä to a
    names_df['name'] = names_df['name'].str.translate(UMLAUTS)

    # decode characters; e.g. á => a
    names_df['name'] = names_df['name'].apply(unidecode)

    # convert name to lowercase (as done for training)
    names_df['name'] = names_df['name'].str.lower()

    # remove all non-alphabetic characters
    names_df['name'] = names_df['name'].str.replace(r'[^\w\s]', '', regex=True)

    # strip whitespaces
    names_df['name'] = names_df['name'].str.strip()

    # split individual characters
    names_df['name'] = names_df['name'].apply(lambda x: list(x))

    # pad names to 50 characters
    name_length = 50
    names_df['name'] = [(name + [' '] * name_length)[:name_length] for name in names_df['name']]

    # encode characters
    names_df['name'] = [[max(0.0, ord(char) - 96.0) for char in name] for name in names_df['name']]

    if train:
        # one-hot encode genders (F: 0.0, M: 1.0)
        names_df['gender'] = [0.0 if gender == 'F' else 1.0 for gender in names_df['gender']]

    return names_df


if __name__ == '__main__':
    print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

    df = pd.read_csv('data/names_binary_ascii.csv')
    # print(df.shape)
    # df.head()

    df = preprocess(df)
    # df.head()

    # initialize model
    model = get_lstm_model(num_alphabets=27, name_length=50, embedding_dim=256)

    # split data into train and test
    X = np.asarray(df['name'].values.tolist())
    y = np.asarray(df['gender'].values.tolist())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # train model
    callbacks = [EarlyStopping(monitor='val_accuracy', min_delta=1e-3, patience=5, mode='max', restore_best_weights=True, verbose=1), ]
    history = model.fit(x=X_train, y=y_train, batch_size=64, epochs=50, validation_data=(X_test, y_test), callbacks=callbacks)

    # save model
    # model.save('data/gender_classifier.h5')
    # print('Saved model to disk')

    # serialize model to JSON
    model_json = model.to_json()
    with open('data/gender_classifier_new.json', 'w') as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights('data/gender_classifier_new.h5')
    print('Saved model to disk')
