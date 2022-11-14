# Token Classification

This directory contains all source code used for the classification of occurring characters in the fan fiction corpus. The classification is done using the pre-trained named entity recognition (NER)
models [Flair](https://github.com/flairNLP/flair) and [spaCy](https://spacy.io).

[token_classifier_batch_flair.py](token_classifier_batch_flair.py): Traverses through all the chapter contents and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in batch mode.

[token_classifier_batch_spacy.py](token_classifier_batch_spacy.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). Results are stored in the associated chapter database documents. This script processes chapters in batch mode.

[token_classifier_batch_spacy_csv.py](token_classifier_batch_spacy_csv.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). CSV files are used as input source. Results are stored as UpdateOne command in a CSV file. This script processes chapters in batch mode.

[token_classifier_iterative_flair.py](token_classifier_iterative_flair.py): Traverses through the chapter contents in a random order and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in iterative mode for being able to lock processed document.

[token_classifier_iterative_flair_stories.py](token_classifier_iterative_flair_stories.py): Traverses through all the chapter contents and tags all person names (PER) using the NER model for German
  with [Flair](https://github.com/flairNLP/flair). For pronouns extraction a [spaCy](https://spacy.io) language model is used. Results are stored in the associated chapter database documents. This script processes
  chapters in iterative mode for being able to lock processed document.

[token_classifier_iterative_spacy.py](token_classifier_iterative_spacy.py): Traverses through all the chapter contents and tags all person names (PER) and pronouns using the NER model for German
  with [spaCy](https://spacy.io). Results are stored in the associated chapter database documents. This script processes chapters in iterative mode for being able to lock processed document.

[cleanse_persons_spacy.py](cleanse_persons_spacy.py): Persons extracted by [spaCy](https://spacy.io) frequently contain verbs and other incorrect text parts. This script removes those.