#!/usr/bin/python3

# -----------------------------------------------------------
# Traverses through all the chapters and stories counting
# sentences, words, letter characters and all characters
# while storing the results for each document.
# -----------------------------------------------------------
from time import sleep

from bson import ObjectId, InvalidBSON
from pymongo import UpdateOne
from tqdm import tqdm
import re
import spacy
import db_connect

db = db_connect.get_database('FanFiction')

try:
    # processing chapters
    chapters = db.chapters.find({'numSentences': None})
    chapter_count = db.chapters.count_documents({'numSentences': None})

    nlp = spacy.load('de_core_news_sm')

    with tqdm(total=chapter_count) as pbar_chapter:
        chapter_updates = []
        for chapter in chapters:
            pbar_chapter.set_description('Processing chapter %s' % chapter['_id'])
            sentence_count = 0
            word_count = 0
            character_letters_count = 0
            character_count = 0
            if 'content' in chapter and isinstance(chapter['content'], str):
                content = chapter['content']

                # count sentences
                doc = nlp(content)
                sentence_tokens = [[token.text for token in sent] for sent in doc.sents]
                sentence_count = len(sentence_tokens)

                # count words
                content_words = re.sub(r'[^\w\s]+', '', content).strip()
                word_count = len(content_words.split())

                # count characters
                content_letters = re.sub(r'\W+', '', content)
                character_count = len(content)
                character_letters_count = len(content_letters)

                # queue for bulk update
                chapter_updates.append(UpdateOne({'_id': chapter['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}}))
                if len(chapter_updates) % 1000 == 0:
                    pbar_chapter.set_description('Writing bulk data')
                    db.chapters.bulk_write(chapter_updates)
                    chapter_updates = []
                pbar_chapter.update(1)
        pbar_chapter.set_description('Writing bulk data')
        db.chapters.bulk_write(chapter_updates)

    # processing stories
    stories_count = db.stories.count_documents({'numSentences': None})
    stories = db.stories.find({'numSentences': None})

    with tqdm(total=stories_count) as pbar_story:
        story_updates = []
        for story in stories:
            pbar_story.set_description('Processing story %s' % story['_id'])
            sentence_count = 0
            word_count = 0
            character_letters_count = 0
            character_count = 0
            story_sums = db.chapters.aggregate([
                {
                    '$match': {'storyId': story['_id'], 'numSentences': {'$exists': True}}
                },
                {
                    '$group': {
                        '_id': '$storyId',
                        'numSentences': {'$sum': '$numSentences'},
                        'numWords': {'$sum': '$numWords'},
                        'numLetters': {'$sum': '$numLetters'},
                        'numCharacters': {'$sum': '$numCharacters'}
                    }
                }
            ])
            if 'numSentences' in story_sums:
                sentence_count = story_sums['numSentences']
            if 'numWords' in story_sums:
                word_count = story_sums['numWords']
            if 'numLetters' in story_sums:
                character_letters_count = story_sums['numLetters']
            if 'numCharacters' in story_sums:
                character_count = story_sums['numCharacters']
            story_updates.append(UpdateOne({'_id': story['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}}))
            if len(story_updates) % 1000 == 0:
                pbar_story.set_description('Writing bulk data')
                db.stories.bulk_write(story_updates)
                story_updates = []
            pbar_story.update(1)
        pbar_story.set_description('Writing bulk data')
        db.stories.bulk_write(story_updates)

finally:
    db_connect.disconnect()
