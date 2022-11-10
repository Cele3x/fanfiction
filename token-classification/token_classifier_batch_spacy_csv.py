# -----------------------------------------------------------
# Traverses through all the chapter contents and tags all
# person names (PER) and pronouns using the NER model for
# German with spaCy. CSV files are used as input source.
# Results are stored as UpdateOne command in a CSV file.
# This script processes chapters in batch mode.
# -----------------------------------------------------------

import csv
import re
from datetime import datetime
from typing import Union
import pandas as pd
import spacy
from bson import ObjectId
from pymongo import UpdateOne
from spacy import Language
from tqdm import tqdm
import os.path
import argparse


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

        return UpdateOne({'_id': chapter_id, 'isTagged': {'$ne': True}}, {'$set': {'persons_spacy': sorted_persons, 'pronouns': pronouns, 'isTagged': True}})
    except Exception as ex:
        print(ex)
        return None


def get_object_id_from_text(text: str) -> ObjectId:
    try:
        hex_value = text[text.find("(")+1:text.find(")")]
        return ObjectId(hex_value)
    except Exception as ex:
        print(ex)
        ObjectId('000000000000000000000000')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", "-f", type=str, nargs='+', required=True)
    args = parser.parse_args()
    for in_filename in args.files:
        out_filename = ('%s_out.csv' % os.path.splitext(in_filename)[0])
        print('%s - Processing %s with output %s...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), in_filename, out_filename))
        out_file_exists = os.path.isfile(out_filename)
        out = open(out_filename, 'a', encoding='UTF8')
        try:
            print('%s - Loading spaCy model...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), end=' ')
            nlp = spacy.load("de_core_news_lg")
            print('Done')

            print('%s - Initializing output file if needed and getting latest ObjectId...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), end=' ')
            writer = csv.writer(out)
            last_object_id = ObjectId('000000000000000000000000')
            if not out_file_exists:  # initialize new output file
                writer.writerow(['_id', 'command'])
            else:  # read output file and store last ObjectId as latest ID
                temp_reader = pd.read_csv(out_filename)
                if '_id' in temp_reader and not temp_reader['_id'].empty:
                    oid = pd.read_csv(out_filename)['_id'].iloc[-1]
                    last_object_id = ObjectId(oid)
                del temp_reader
            print('Done')

            print('%s - Reading CSV input file...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), end=' ')
            reader = pd.read_csv(in_filename)
            print('Done')

            with tqdm(total=len(reader.index)) as pbar:
                for index, row in reader.iterrows():
                    if '_id' in row and 'content' in row:
                        object_id = get_object_id_from_text(row['_id'])
                        if object_id <= last_object_id:
                            pbar.set_description('Skipping %s' % object_id)
                            pbar.update(1)
                            continue

                        pbar.set_description('Processing %s' % object_id)
                        update = get_chapter_tags(nlp, object_id, row['content'])
                        if update:
                            writer.writerow([object_id, update])

                    pbar.update(1)
        except Exception as e:
            print(e)
            out.close()
    print('%s - Done processing all input files!' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
