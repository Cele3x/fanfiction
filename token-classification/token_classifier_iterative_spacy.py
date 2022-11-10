# -----------------------------------------------------------
# Traverses through all the chapter contents and tags all
# person names (PER) and pronouns using the NER model for
# German with spaCy. Results are stored in the associated
# chapter database documents. This script processes chapters
# in iterative mode for being able to lock processed
# document.
# -----------------------------------------------------------

import re
from datetime import datetime
import spacy
from bson import ObjectId
from spacy import Language

from utils.db_connect import DatabaseConnection


def set_chapter_tags(spacy_nlp: Language, chapter_id: ObjectId, chapter_content: str):
    """Processes each sentence in the provided text, counting the number of 3rd person singular pronouns and person names appearing.

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

        db.chapters.update_one({'_id': chapter_id, 'isTagged': {'$ne': True}}, {'$set': {'persons_spacy': sorted_persons, 'pronouns': pronouns, 'isTagged': True, 'isLocked': False}})
    except Exception as ex:
        print(ex)
        return None


if __name__ == "__main__":
    client = DatabaseConnection()
    db_updates = []
    db = None
    try:
        print('%s - Start processing with SpaCy...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
        avg_processing_time = 0
        processing_times = []

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        # load tagger
        nlp = spacy.load("de_core_news_lg")

        chapter_count = db.chapters.count_documents({'isTagged': {'$ne': True}})
        print('Chapters: %i' % chapter_count)

        while True:
            start_time = datetime.now()
            chapter = db.chapters.find_one_and_update({'isTagged': {'$ne': True}, 'isLocked': {'$ne': True}}, {'$set': {'isLocked': True}})
            if chapter is None:
                break

            print('[S] %s --- Chapter %s - Chunk %i...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), chapter['_id'], chapter['chunk']), end=' ', flush=True)
            set_chapter_tags(nlp, chapter['_id'], chapter['content'])
            print('DONE [%is]' % (datetime.now() - start_time).seconds)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
