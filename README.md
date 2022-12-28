# Acquisition of a German Fan Fiction Corpus and Analysis in the Context of Gender Representation

This repository was used for the master thesis "Acquisition of a German Fan Fiction Corpus and Analysis in the Context of Gender Representation" at the University of Regensburg.
It contains all source code necessary to reproduce the results of the thesis.

## [Submission](submission)

This directory contains the final submission of the thesis.

**Content**

- [Sasse_Jonathan_Masters_Thesis.pdf](submission/Sasse_Jonathan_Masters_Thesis.pdf): Final thesis document.
- [figures.md](submission/figures.md): Contains all figures from database queries listed in [Data Analysis](data-analysis).

## [Data Acquisition](data-acquisition)

This directory contains the source code for the data acquisition. The web scrapers for acquiring fan fiction data is written in Python and uses the [Scrapy](https://scrapy.org) framework.
There are multiple Spiders for the archives [FanFiktion.de](https://www.fanfiktion.de/) and [ArchiveOfOurOwn](https://archiveofourown.org).

**Content**

- [Spiders](data-acquisition/spiders)
    - [FanFiktion.py](data-acquisition/spiders/FanFiktion.py): Spider for the archive FanFiktion.de.
    - [ArchiveOfOurOwn.py](data-acquisition/spiders/ArchiveOfOurOwn.py): Spider for the archive ArchiveOfOurOwn.
    - [FanFiktionHtml.py](data-acquisition/spiders/FanFiktionHtml.py): Spider for the archive FanFiktion.de, which uses the HTML files previously downloaded.
    - [FanFiktionMissing.py](data-acquisition/spiders/FanFiktionMissing.py): Spider for the archive FanFiktion.de, scraping missing data.
    - [ArchiveOfOurOwnMissing.py](data-acquisition/spiders/ArchiveOfOurOwnMissing.py): Spider for the archive ArchiveOfOurOwn, scraping missing data.
- [Scripts](data-acquisition/scripts)
    - [extract_archives.py](data-acquisition/scripts/extract_archives.py): Extracts archives from an HTML downloader Spider links their filepath inside the database.
    - [generate_csv.py](data-acquisition/scripts/generate_csv.py): Extracts filenames from archives files and derives urls from them. The gathered information are being stored in csv-files for stories, users and reviews
      accordingly.
    - [rearchive.py](data-acquisition/scripts/rearchive.py): Extracts archives for storing them in a new archive consisting of 1,000 files.
    - [match_fandoms.py](data-acquisition/scripts/match_fandoms.py): Compares FF.de and AO3 fandoms and tries to match those storing them in a CSV file.
    - [rename_fandoms.py](data-acquisition/scripts/rename_fandoms.py): Uses the CSV file generated in match_fandoms.py to rename AO3 fandoms matching the FF.de names.
    - [simple_scraper.py](data-acquisition/scripts/simple_scraper.py): Simple scraper using BeautifulSoup for filling smaller data gaps in previously crawled data.

## [Token Classification](token-classification)

This directory contains all source code used for the classification of occurring characters in the fan fiction corpus. The classification is done using the pre-trained named entity recognition (NER)
models [Flair](https://github.com/flairNLP/flair) and [spaCy](https://spacy.io).

**Content**

- [token_classifier_batch_flair.py](token-classification/token_classifier_batch_flair.py): Traverses through all the chapter contents and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in batch mode.
- [token_classifier_batch_spacy.py](token-classification/token_classifier_batch_spacy.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). Results are stored in the associated chapter database documents. This script processes chapters in batch mode.
- [token_classifier_batch_spacy_csv.py](token-classification/token_classifier_batch_spacy_csv.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). CSV files are used as input source. Results are stored as UpdateOne command in a CSV file. This script processes chapters in batch mode.
- [token_classifier_iterative_flair.py](token-classification/token_classifier_iterative_flair.py): Traverses through the chapter contents in a random order and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in iterative mode for being able to lock processed document.
- [token_classifier_iterative_flair_stories.py](token-classification/token_classifier_iterative_flair_stories.py): Traverses through all the chapter contents and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in iterative mode for being able to lock processed document.
- [token_classifier_iterative_spacy.py](token-classification/token_classifier_iterative_spacy.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). Results are stored in the associated chapter database documents. This script processes chapters in iterative mode for being able to lock processed document.
- [cleanse_persons_spacy.py](token-classification/cleanse_persons_spacy.py): Persons extracted by [spaCy](https://spacy.io) frequently contain verbs and other incorrect text parts. This script removes those.

## [Gender Classification](gender-classification)

This directory contains all source code used for predicting previously tagged person tokens (PER) by the NER models.
Character genders are predicted after training a LSTM model using [TensorFlow](https://www.tensorflow.org) and [Keras](https://keras.io).
Names for training the model were acquired from the [NLTK](http://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/nlp/corpora/names/)
corpus, [US Baby Names from Social Security Card Applications](https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-data) and scraped from [babynames.com](https://babynames.com).

**Content**

- [selenium_name_scraper.py](gender-classification/selenium_name_scraper.py): Selenium scraper for extracting names with gender from babynames.com.
- [train_gender_classifier.py](gender-classification/train_gender_classifier.py): Train gender classifier LSTM model using TensorFlow and Keras.
- [merge_story_persons.py](gender-classification/merge_story_persons.py): Merges all persons from chapters into the story document. Person names get cleansed in the process.
- [predict_person_genders.py](gender-classification/predict_person_genders.py): Traverse the character names list and predict their gender.
- [set_person_genders.py](gender-classification/set_person_genders.py): Sets and counts gender occurrences for stories using the previously predicted names list.

## [Data Analysis](data-analysis)

All queries for tables and figures used in the thesis are listed in this directory. They are structured after their purpose and displayed in a Markdown document.

**Content**

- [General Stats Queries](data-analysis/general_stats_queries.md): Queries for acquiring general corpus statistics.
- [Story Queries](data-analysis/story_queries.md): Queries for pairing, rating and character frequency statistics.
- [Content Length Queries](data-analysis/content_lengths_queries.md): Queries for content length statistics.
- [Fandom Genre Queries](data-analysis/fandom_genre_queries.md): Queries for fandom and genre statistics.
- [Character Gender Queries](data-analysis/character_gender_queries.md): Queries for character gender distributions in general and for popular fandoms.
- [Pronoun Queries](data-analysis/pronoun_queries.md): Queries for gender representation per pronoun usage with and without genre.
- [User Gender Queries](data-analysis/user_gender_queries.md): Queries for user statistics on FanFiktion.de.

## Miscellaneous

- [utils/db_connect.py](utils/db_connect.py): Provides functions for connecting to and disconnecting from a MongoDB database while using environment specific variables.
- [scripts/restructure_db.py](scripts/restructure_db.py): Restructures the database from a relational database structure to a non-relational MongoDB database for being able to use the full MongoDB performance and
  functionality bandwidth.
- [scripts/set_content_lengths.py](scripts/set_content_lengths.py): Traverses through all the chapters and stories counting sentences, words, letter characters and all characters while storing the results for each
  document.
