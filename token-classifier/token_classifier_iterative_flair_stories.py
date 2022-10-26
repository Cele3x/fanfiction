# -----------------------------------------------------------
# Traverses through all the chapter contents and tags all
# person names (PER) using the NER model for German with
# Flair. For pronouns extraction a spaCy language model is
# used. Results are stored in the associated chapter database
# documents. This script processes chapters in iterative
# mode for being able to lock processed document.
# -----------------------------------------------------------

import re
from datetime import datetime
import spacy
from bson import ObjectId
from pymongo.client_session import ClientSession
from spacy import Language
import pymongo
import urllib.parse
from pymongo import UpdateOne
from flair.data import Sentence, DT
from flair.models import SequenceTagger
from flair.nn import Model
import os
from typing import Optional


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
        chapter_start = datetime.now()
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

        chapter_elapsed = (datetime.now() - chapter_start).total_seconds()

        return UpdateOne({'_id': chapter_id}, {'$set': {'persons': sorted_persons, 'isTagged': True, 'isLocked': False, 'processingTime': chapter_elapsed}})
    except Exception as ex:
        print(ex)


def write_to_database(db_session: ClientSession, updates: list, process_id: int, current_index: int):
    try:
        print('[%i - %i] %s --- Bulk writing %d updates to database' % (process_id, current_index, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(updates)))
        db.chapters.bulk_write(updates, session=db_session)
    except Exception as ex:
        print(ex)
        print(updates)


if __name__ == "__main__":
    uri = 'mongodb://%s:%s@%s:%s' % (urllib.parse.quote_plus('jonathan'), urllib.parse.quote_plus('Z#0%H*c0%0#4rK!9CU'), 'liquid-vanilla.com', '27017')
    client = pymongo.MongoClient(uri)
    db_updates = []
    try:
        pid = os.getpid()
        print('[%i] %s --- Start processing with flairNLP...' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())))

        db = client['FanFiction']
        if db is None:
            raise Exception('Database connection failed.')

        # load tagger
        tagger = SequenceTagger.load("flair/ner-multi-fast")
        nlp = spacy.load("de_core_news_lg")
        print('[%i] %s --- Loaded flairNLP and spaCy models' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())))

        with client.start_session() as session:
            i = 0
            while True:
                i = i + 1
                start_time = datetime.now()
                refresh_time = datetime.now()

                story = db.stories.find_one_and_update({'isTaggedPartially': True, 'isLocked': False}, {'$set': {'isLocked': True}}, session=session)
                if story is None:
                    break

                print('[%i - %i] %s --- Story %s...' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), story['_id']), flush=True)

                chapters = db.chapters.find({'storyId': story['_id'], 'isTagged': False}, session=session, no_cursor_timeout=True)
                db_updates = []
                for chapter in chapters:
                    if (datetime.now() - refresh_time).seconds > 600:
                        print('[%i - %i] %s --- Refreshing session' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())), flush=True)
                        client.admin.command({'refreshSessions': [session.session_id]})
                        refresh_time = datetime.now()

                    print('[%i - %i] %s --- > Chapter %s...' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), chapter['_id']), end=' ', flush=True)
                    update = set_chapter_tags(tagger, nlp, chapter['_id'], chapter['content'])
                    print('DONE')
                    if update:
                        db_updates.append(update)

                write_to_database(session, db_updates, pid, i)
                elapsed = (datetime.now() - start_time).total_seconds()
                db.stories.update_one({'_id': story['_id']}, {'$set': {'isTaggedPartially': False, 'isLocked': False, 'isTagged': True, 'processingTime': elapsed}}, session=session)

                print('[%i - %i] %s --- Story %s... DONE [%0.2fs]' % (pid, i, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), story['_id'], elapsed), flush=True)

        print('[%i] %s --- Finished after %i iterations' % (pid, '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), i))
    except Exception as e:
        print(e)
        print('UPDATES: %s' % db_updates)
    finally:
        client.close()
