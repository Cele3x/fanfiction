# -----------------------------------------------------------
# Traverses through the chapter contents in a random order
# and tags all person names (PER) using the NER model for
# German with Flair. For pronouns extraction a spaCy language
# model is used. Results are stored in the associated chapter
# database documents. This script processes chapters in
# iterative mode for being able to lock processed document.
# -----------------------------------------------------------

import re
from datetime import datetime
import spacy
from bson import ObjectId
from spacy import Language
from pymongo import UpdateOne
from flair.data import Sentence, DT
from flair.models import SequenceTagger
from flair.nn import Model
import os
from typing import Optional
from random import choice
from utils.db_connect import DatabaseConnection


def set_chapter_tags(flair_tagger: Model[DT], spacy_nlp: Language, chapter_id: ObjectId, chapter_content: str) -> Optional[UpdateOne]:
    """Processes each sentence in the provided text, counting the number of 3rd person singular pronouns and person names appearing.

    :param flair_tagger: Model[DT]
        for text classification provided by flair
    :param spacy_nlp: Language
        model provided by spaCy
    :param chapter_id: ObjectId
        referencing the processed chapter document from the database
    :param chapter_content: str
        containing the chapter text for the token extraction
    """
    try:
        doc = spacy_nlp(chapter_content)

        # init result variables
        persons = {}

        for sentence in doc.sents:
            flair_sentence = Sentence(text=sentence.text, language_code='de')
            flair_tagger.predict(flair_sentence)

            # iterate over entities and store PER tags
            for entity in flair_sentence.get_spans('ner'):
                if entity.tag == 'PER' and entity.score > 0.5:
                    # remove preceding and trailing punctuations
                    name = re.sub(r'^\W+|\W+$', '', entity.text)
                    if name in persons.keys():
                        persons[name] = persons[name] + 1
                    else:
                        persons[name] = 1

        # sort persons and merge where possible
        sorted_persons = dict(sorted(persons.items(), key=lambda x: x[1], reverse=True))
        for person in list(sorted_persons):
            person_singular = re.sub(r's$', '', person)
            if person != person_singular and person_singular in sorted_persons.keys():
                sorted_persons[person_singular] = sorted_persons[person_singular] + sorted_persons[person]
                del sorted_persons[person]

        return UpdateOne({'_id': chapter_id}, {'$set': {'persons': sorted_persons, 'isTagged': True, 'isLocked': False}})
    except Exception as ex:
        print(ex)


def write_to_database(updates: list, process_id: int, current_index: int):
    try:
        print('[%i - %i] %s --- Bulk writing %d updates to database' % (process_id, current_index, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(updates)))
        db.chapters.bulk_write(updates)
    except Exception as ex:
        print(ex)
        print(updates)


if __name__ == "__main__":
    client = DatabaseConnection()
    try:
        pid = os.getpid()
        print('[%i] %s --- Start processing with flairNLP...' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load tagger
        tagger = SequenceTagger.load("flair/ner-multi-fast")
        nlp = spacy.load("de_core_news_lg")
        print('[%i] %s --- Loaded flairNLP and spaCy models' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())))

        i = 0
        db_updates = []
        open_chunks = list(range(1, 196))
        chunk = 0
        while True:
            i = i + 1
            start_time = datetime.now()
            if not open_chunks:
                write_to_database(db_updates, pid, i)
                break

            chunk = choice(open_chunks)
            chapter = db.chapters.find_one_and_update({'isTagged': False, 'isLocked': False, 'chunk': chunk}, {'$set': {'isLocked': True}})
            if chapter is None:
                print('[%i - %i] %s --- Chunk %i processed - %i remaining' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), chunk, len(open_chunks)))
                if chunk in open_chunks:
                    open_chunks.remove(chunk)
                continue

            update = set_chapter_tags(tagger, nlp, chapter['_id'], chapter['content'])
            if update:
                db_updates.append(update)
            elapsed = (datetime.now() - start_time).total_seconds()
            print('[%i - %i] %s --- Chapter %s - Chunk %i... DONE [%0.2fs]' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), chapter['_id'], chapter['chunk'], elapsed), flush=True)

            if i % 50 == 0:
                write_to_database(db_updates, pid, i)
                db_updates = []
        print('[%i] %s --- Finished after %i iterations' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), i))
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
