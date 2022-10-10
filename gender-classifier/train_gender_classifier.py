# -----------------------------------------------------------
# Train gender classifier model.
# -----------------------------------------------------------

import tensorflow as tf

keras = tf.keras
import pandas as pd
from keras import Sequential
from keras.layers import Embedding, Bidirectional, LSTM, Dense
from keras.optimizers import Adam
import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping


def lstm_model(num_alphabets=27, name_length=50, embedding_dim=256):
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
    # Step 1: Lowercase
    names_df['name'] = names_df['name'].str.lower()

    # Step 2: Split individual characters
    names_df['name'] = [list(name) for name in names_df['name']]

    # Step 3: Pad names with spaces to make all names same length
    name_length = 50
    names_df['name'] = [
        (name + [' '] * name_length)[:name_length]
        for name in names_df['name']
    ]

    # Step 4: Encode Characters to Numbers
    names_df['name'] = [
        [
            max(0.0, ord(char) - 96.0)
            for char in name
        ]
        for name in names_df['name']
    ]

    if train:
        # Step 5: Encode Gender to Numbers
        names_df['gender'] = [
            0.0 if gender == 'F' else 1.0
            for gender in names_df['gender']
        ]

    return names_df


if __name__ == '__main__':
    df = pd.read_csv('data/uniq_names_bi_ascii_v2.csv')
    print(df.shape)
    df.head()

    df = preprocess(df)
    df.head()

    # Step 1: Instantiate the model
    model = lstm_model(num_alphabets=27, name_length=50, embedding_dim=256)

    # Step 2: Split Training and Test Data
    X = np.asarray(df['name'].values.tolist())
    y = np.asarray(df['gender'].values.tolist())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Step 3: Train the model
    callbacks = [
        EarlyStopping(monitor='val_accuracy', min_delta=1e-3, patience=5, mode='max', restore_best_weights=True, verbose=1),
    ]

    history = model.fit(x=X_train, y=y_train, batch_size=64, epochs=50, validation_data=(X_test, y_test), callbacks=callbacks)

    # Step 4: Save the model
    model.save('gender_classifier.h5')

    # Step 5: Plot accuracies
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='val')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # serialize model to JSON
    model_json = model.to_json()
    with open("gender_classifier.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("gender_classifier.h5")
    print("Saved model to disk")
