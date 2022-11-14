# Gender Classification

This directory contains all source code used for predicting all previously tagged person tokens (PER) by the NER models.
Character genders are predicted after training a LSTM model using [TensorFlow](https://www.tensorflow.org) and [Keras](https://keras.io).
Names for the training are using the [NLTK](http://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/nlp/corpora/names/)
corpus, [US Baby Names from Social Security Card Applications](https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-data) and scraped from [babynames.com](https://babynames.com).


[selenium_name_scraper.py](selenium_name_scraper.py): Selenium scraper for extracting names with gender from babynames.com.

[train_gender_classifier.py](train_gender_classifier.py): Train gender classifier LSTM model using TensorFlow and Keras.

[merge_story_persons.py](merge_story_persons.py): Merges all persons from chapters into the story document. Person names get cleansed in the process.

[predict_person_genders.py](predict_person_genders.py): Traverse the character names list and predict their gender.

[set_person_genders.py](set_person_genders.py): Sets and counts gender occurrences for stories using the previously predicted names list.