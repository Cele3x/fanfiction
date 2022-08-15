#!/usr/bin/python3

# -----------------------------------------------------------
# Traverses through all the chapters and stories counting
# sentences, words, letter characters and all characters
# while storing the results for each document.
# -----------------------------------------------------------

from tqdm import tqdm
import re
import spacy
import db_connect

db = db_connect.get_database('FanfictionDB_refactor')

try:
    # processing chapters
    chapters = db.chapters.find({'numSentences': None})
    chapter_count = db.chapters.count_documents({'numSentences': None})

    nlp = spacy.load('de_core_news_sm')

    with tqdm(total=chapter_count) as pbar_chapter:
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

                # save to database
                db.chapters.update_one({'_id': chapter['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}})

            pbar_chapter.update(1)

    # processing stories
    stories_count = db.stories.count_documents({'numSentences': None})
    stories = db.stories.aggregate([
        {
            '$lookup': {
                'from': 'chapters',
                'localField': '_id',
                'foreignField': 'storyId',
                'as': 'chapter'
            }
        },
        {
            '$match': {'numSentences': None, 'chapter.numSentences': {'$exists': True}}
        },
        {
            '$project': {
                '_id': 1,
                'numSentences': {'$sum': '$chapter.numSentences'},
                'numWords': {'$sum': '$chapter.numWords'},
                'numLetters': {'$sum': '$chapter.numLetters'},
                'numCharacters': {'$sum': '$chapter.numCharacters'}
            }
        },
    ])

    with tqdm(total=stories_count) as pbar_story:
        for story in stories:
            pbar_story.set_description('Processing story %s' % story['_id'])
            sentence_count = 0
            word_count = 0
            character_letters_count = 0
            character_count = 0
            if 'numSentences' in story:
                sentence_count = story['numSentences']
            if 'numWords' in story:
                word_count = story['numWords']
            if 'numLetters' in story:
                character_letters_count = story['numLetters']
            if 'numCharacters' in story:
                character_count = story['numCharacters']
            db.stories.update_one({'_id': story['_id']}, {'$set': {'numSentences': sentence_count, 'numWords': word_count, 'numLetters': character_letters_count, 'numCharacters': character_count}})

            pbar_story.update(1)

finally:
    db_connect.disconnect()
