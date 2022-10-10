# -----------------------------------------------------------
# Traverses through all the chapter contents and tags all
# person names (PER) and pronouns using the NER model for
# German with spaCy. Results are stored in the associated
# chapter database documents. This script processes
# chapters in batch mode.
# -----------------------------------------------------------

import re
from datetime import datetime, timedelta
from math import ceil
from typing import Union

import spacy
from bson import ObjectId
from pymongo import UpdateOne, DESCENDING
from spacy import Language
from tqdm import tqdm

from scripts.db_connect import DatabaseConnection


def get_chapter_tags(spacy_nlp: Language, chapter_id: ObjectId, chapter_content: str) -> Union[None, UpdateOne]:
    """Processes each sentence in the provided text, counting the number of 3rd person singular pronouns and person names appearing.

    :param spacy_nlp: Language
        model provided by spaCy
    :param chapter_id: ObjectId
        referencing the processed chapter document from the database
    :param chapter_content: str
        containing the chapter text for the token extraction
    :return: None | UpdateOne
        command for bulk writing to the database
    """
    try:
        doc = spacy_nlp(chapter_content)

        # init result variables
        persons = {}
        pronouns = {'er': 0, 'sie': 0, 'seiner': 0, 'ihrer': 0, 'ihm': 0, 'ihr': 0, 'ihn': 0}

        for sentence in doc.sents:
            s = spacy_nlp(sentence.text)

            # iterate over entities and store PER tags
            for entity in s.ents:
                if entity.label_ == 'PER':
                    # remove preceding and trailing punctuations
                    name = re.sub(r'^\W+|\W+$', '', entity.text)
                    if name in persons.keys():
                        persons[name] = persons[name] + 1
                    else:
                        persons[name] = 1

            # iterate over each word and store PRON tags
            for item in sentence:
                m_result = item.morph
                pron_type = m_result.get('PronType')
                person = m_result.get('Person')
                number = m_result.get('Number')
                text_lower = item.text.lower()
                if pron_type == ['Prs'] and number == ['Sing'] and person == ['3'] and text_lower in pronouns.keys():
                    pronouns[text_lower] = pronouns[text_lower] + 1

        # sort persons and merge where possible
        sorted_persons = dict(sorted(persons.items(), key=lambda x: x[1], reverse=True))
        for person in list(sorted_persons):
            person_singular = re.sub(r's$', '', person)
            if person != person_singular and person_singular in sorted_persons.keys():
                sorted_persons[person_singular] = sorted_persons[person_singular] + sorted_persons[person]
                del sorted_persons[person]

        # print(sorted_persons)

        return UpdateOne({'_id': chapter_id}, {'$set': {'persons_spacy': sorted_persons, 'pronouns': pronouns, 'isTagged': True}})
    except Exception as ex:
        print(ex)
        return None


if __name__ == "__main__":
    client = DatabaseConnection()
    db_updates = []
    db = None
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
        avg_processing_time = 0
        processing_times = []

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load tagger
        # tagger = SequenceTagger.load("flair/ner-german-large")
        nlp = spacy.load("de_core_news_lg")

        chapter_count = db.chapters.count_documents({'isTagged': {'$ne': True}})
        print('Chapters: %i' % chapter_count)

        batchsize = 250
        for i in range(0, chapter_count, batchsize):
            batch_start_time = datetime.now()
            db_updates = []
            chapters = db.chapters.find({'isTagged': {'$ne': True}}, no_cursor_timeout=True).sort([('_id', DESCENDING)]).limit(batchsize)
            with tqdm(total=batchsize) as pbar:
                batch_current = i / batchsize + 1
                batch_total = ceil(chapter_count / batchsize)
                for chapter in chapters:
                    pbar.set_description('Batch %i/%i - Chunk %i' % (batch_current, batch_total, chapter['chunk']))
                    update = get_chapter_tags(nlp, chapter['_id'], chapter['content'])
                    if update:
                        db_updates.append(update)
                    pbar.update(1)

            print('%s - Bulk writing %d updates to database' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_updates)))
            db.chapters.bulk_write(db_updates)
            chapters.close()

            processing_time = (datetime.now() - batch_start_time).seconds
            processing_time_per_chapter = processing_time / batchsize
            processing_times.append(processing_time_per_chapter)
            avg_processing_time = sum(processing_times) / len(processing_times)
            est_processing_time = timedelta(seconds=chapter_count * avg_processing_time)
            print('Processing times - per batch: %ds | per chapter: %0.2fs | average per chapter: %0.2fs' % (processing_time, processing_time_per_chapter, avg_processing_time))
            print('Estimated total processing time: %s' % est_processing_time)
    except KeyboardInterrupt as ki:
        if db is not None and db_updates:
            print('%s - Bulk writing %d updates to database' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_updates)))
            db.chapters.bulk_write(db_updates)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
