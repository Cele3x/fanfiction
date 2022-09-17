#!/usr/bin/env python3

# -----------------------------------------------------------
# Traverses through all the chapter contents and tags all
# person names (PER) using the NER model for German with
# Flair. For pronouns extraction a spaCy language model is
# used. Results are stored in the associated chapter database
# documents. This script uses a multiprocessing approach.
# -----------------------------------------------------------

import re
from datetime import datetime, timedelta
from math import ceil
from typing import Union

import spacy
from bson import ObjectId
from flair.data import Sentence, DT
from flair.models import SequenceTagger
from flair.nn import Model
from pymongo import UpdateOne, DESCENDING
from spacy import Language
from tqdm import tqdm
from multiprocessing import Pool, cpu_count, freeze_support

from db_connect import DatabaseConnection


def get_chapter_tags(flair_tagger: Model[DT], spacy_nlp: Language, chapter_id: ObjectId, chapter_content: str) -> Union[None, UpdateOne]:
    """Processes each sentence in the provided text, counting the number of 3rd person singular pronouns and person names appearing.

    :param flair_tagger: Model[DT]
        for text classification provided by flair
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
            flair_sentence = Sentence(sentence.text)
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

        return UpdateOne({'_id': chapter_id}, {'$set': {'persons': sorted_persons, 'pronouns': pronouns, 'isTagged': True}})
    except Exception as ex:
        print(ex)
        return None


if __name__ == "__main__":
    freeze_support()
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
        avg_processing_time = 0
        processing_times = []

        print('%s - Number of CPUs: %i' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), cpu_count()))
        process_count = 2  # cpu_count()
        print('%s - Used CPUs: %i' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), process_count))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load tagger
        taggers = [SequenceTagger.load("flair/ner-multi-fast") for i in range(0, process_count)]
        nlps = [spacy.load("de_core_news_lg") for i in range(0, process_count)]

        chapter_count = db.chapters.count_documents({'isTagged': {'$ne': True}})
        print('Chapters: %i' % chapter_count)

        batchsize = process_count * 16
        for i in range(0, chapter_count, batchsize):
            batch_start_time = datetime.now()
            chapters = db.chapters.find({'isTagged': {'$ne': True}}).limit(batchsize).sort([('numSentences', DESCENDING)])  # sort for optimized process load distribution
            chapter_tuples = [(taggers[idx % process_count], nlps[idx % process_count], chapter['_id'], chapter['content']) for idx, chapter in enumerate(chapters)]
            status_desc = 'Batch %i/%i' % (i / batchsize + 1, ceil(chapter_count / batchsize))

            with Pool(process_count) as mp_pool:
                result = mp_pool.starmap_async(get_chapter_tags, tqdm(chapter_tuples, total=len(chapter_tuples), desc=status_desc), chunksize=16)
                result.wait()
                results_filtered = list(filter(None, result.get()))
                if results_filtered:
                    print('%s - Bulk writing %d updates to database' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(results_filtered)))
                    db.chapters.bulk_write(results_filtered)

            processing_time = (datetime.now() - batch_start_time).seconds
            processing_time_per_chapter = processing_time / batchsize
            processing_times.append(processing_time_per_chapter)
            avg_processing_time = sum(processing_times) / len(processing_times)
            est_processing_time = timedelta(seconds=chapter_count * avg_processing_time)
            print('Processing times - per batch: %ds | per chapter: %0.2fs | average per chapter: %0.2fs' % (processing_time, processing_time_per_chapter, avg_processing_time))
            print('Estimated total processing time: %s' % est_processing_time)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
