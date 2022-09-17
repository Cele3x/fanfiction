#!/usr/bin/python3

# -----------------------------------------------------------
# Restructures the database from a relational database
# structure to a non-relational MongoDB database for being
# able to use the full MongoDB performance and functionality
# bandwidth.
# -----------------------------------------------------------

from pymongo import IndexModel, ASCENDING
from tqdm import tqdm
from db_connect import DatabaseConnection

client = DatabaseConnection()
db = client.connect('FanFiction')

try:
    # STORIES
    print('Processing stories...')

    # copy stories to new table
    db.temp_stories.drop()
    db.stories.aggregate([{'$match': {}}, {'$out': 'temp_stories'}])

    # set association fields
    # - source
    story_sources = db.temp_stories.aggregate([{'$group': {'_id': "$sourceId"}}])
    for story_source in story_sources:
        source = db.sources.find_one({'_id': story_source['_id']})
        if source:
            db.temp_stories.update_many({'sourceId': source['_id']}, {'$set': {'source': source['name']}})

    # - category
    story_categories = db.temp_stories.aggregate([{'$group': {'_id': "$categoryId"}}])
    story_category_count = len(list(db.temp_stories.aggregate([{'$group': {'_id': "$categoryId"}}])))  # list() consumes Cursor
    with tqdm(total=story_category_count) as pbar_category:
        pbar_category.set_description('Processing categories')
        for story_category in story_categories:
            pbar_category.update(1)
            category = db.categories.find_one({'_id': story_category['_id']})
            if category:
                db.temp_stories.update_many({'categoryId': category['_id']}, {'$set': {'category': category['name1']}})

    # - genre
    story_genres = db.temp_stories.aggregate([{'$group': {'_id': "$genreId"}}])
    story_genre_count = len(list(db.temp_stories.aggregate([{'$group': {'_id': "$genreId"}}])))
    with tqdm(total=story_genre_count) as pbar_genre:
        pbar_genre.set_description('Processing genres')
        for story_genre in story_genres:
            pbar_genre.update(1)
            genre = db.genres.find_one({'_id': story_genre['_id']})
            if genre:
                db.temp_stories.update_many({'genreId': genre['_id']}, {'$set': {'genre': genre['name1']}})

    # - pairings
    pairings = db.pairings.find({})
    pairing_count = db.pairings.count_documents({})
    with tqdm(total=pairing_count) as pbar_pairing:
        pbar_pairing.set_description('Processing pairings')
        for pairing in pairings:
            pbar_pairing.update(1)
            db.temp_stories.update_many({'pairingId': pairing['_id']}, {'$set': {'pairings': [pairing['name2']]}})
            story_pairings = db.story_pairings.find({'pairingId': pairing['_id']}).distinct('storyId')
            db.temp_stories.update_many({'_id': {'$in': story_pairings}}, {'$addToSet': {'pairings': pairing['name2']}})

    # - ratings
    ratings = db.ratings.find({})
    rating_count = db.ratings.count_documents({})
    with tqdm(total=rating_count) as pbar_rating:
        pbar_rating.set_description('Processing ratings')
        for rating in ratings:
            pbar_rating.update(1)
            db.temp_stories.update_many({'ratingId': rating['_id']}, {'$set': {'ratings': [rating['name1']]}})
            story_ratings = db.story_ratings.find({'ratingId': rating['_id']}).distinct('storyId')
            db.temp_stories.update_many({'_id': {'$in': story_ratings}}, {'$addToSet': {'ratings': rating['name1']}})

    # - fandoms
    fandoms = db.fandoms.find({})
    fandom_count = db.fandoms.count_documents({})
    with tqdm(total=fandom_count) as pbar_fandom:
        pbar_fandom.set_description('Processing fandoms')
        for fandom in fandoms:
            pbar_fandom.update(1)
            story_fandoms = db.story_fandoms.find({'fandomId': fandom['_id']}).distinct('storyId')
            tiers = []
            fandom_item = {}
            if 'tier1' in fandom and fandom['tier1'] is not None:
                tiers.append(' || '.join(fandom['tier1']))
                fandom_item['tier1'] = ' || '.join(fandom['tier1'])
            if 'tier2' in fandom and fandom['tier2'] is not None:
                tiers.append(' || '.join(fandom['tier2']))
                fandom_item['tier2'] = ' || '.join(fandom['tier2'])
            if 'tier3' in fandom and fandom['tier3'] is not None:
                tiers.append(' || '.join(fandom['tier3']))
                fandom_item['tier3'] = ' || '.join(fandom['tier3'])
            fandom_item['name'] = ' - '.join(tiers)
            db.temp_stories.update_many({'_id': {'$in': story_fandoms}}, {'$addToSet': {'fandoms': fandom_item}})

    # - tags
    tags = db.tags.find({})
    tag_count = db.tags.count_documents({})
    with tqdm(total=tag_count) as pbar_tag:
        pbar_tag.set_description('Processing tags')
        for tag in tags:
            pbar_tag.update(1)
            story_tags = db.story_tags.find({'tagId': tag['_id']}).distinct('storyId')
            db.temp_stories.update_many({'_id': {'$in': story_tags}}, {'$addToSet': {'tags': tag['name1']}})

    # - topics
    topics = db.topics.find({})
    topic_count = db.topics.count_documents({})
    with tqdm(total=topic_count) as pbar_topic:
        pbar_topic.set_description('Processing topics')
        for topic in topics:
            pbar_topic.update(1)
            story_topics = db.story_topics.find({'topicId': topic['_id']}).distinct('storyId')
            db.temp_stories.update_many({'_id': {'$in': story_topics}}, {'$addToSet': {'topics': topic['name1']}})

    # - characters
    characters = db.characters.find({})
    character_count = db.characters.count_documents({})
    with tqdm(total=character_count) as pbar_character:
        pbar_character.set_description('Processing characters')
        for character in characters:
            pbar_character.update(1)
            story_characters = db.story_characters.find({'characterId': character['_id']}).distinct('storyId')
            fandom_name = None
            if 'fandomId' in character:
                fandom = db.fandoms.find_one({'_id': character['fandomId']})
                if fandom:
                    fandom_name = ' || '.join(fandom['tier1']) if 'tier1' in fandom else ' || '.join(fandom['name1'])
            db.temp_stories.update_many({'_id': {'$in': story_characters}}, {'$addToSet': {'characters': {'fandom': fandom_name, 'character': character['name1']}}})

    # remove unused fields
    unset_fields = {'currentChapterCount': 1,
                    'currentReviewCount': 1,
                    'isPreliminary': 1,
                    'fandom': 1,
                    'totalChapterCount': 1,
                    'totalReviewCount': 1,
                    'sourceId': 1,
                    'categoryId': 1,
                    'genreId': 1,
                    'pairingId': 1,
                    'ratingId': 1,
                    'hasMissingChapters': 1,
                    'isRedirected': 1,
                    'redirectedFrom': 1,
                    'redirectedTo': 1,
                    'isLocked': 1,
                    'ageVerification': 1}
    db.temp_stories.update_many({}, {'$unset': unset_fields})

    print('Done!\n')

    # CHAPTERS
    print('Processing chapters...')

    # drop all indexes
    db.chapters.drop_indexes()

    # remove unused fields
    unset_fields = {'isPreliminary': 1,
                    'hasMissingContent': 1,
                    'notFound': 1,
                    'isRedirected': 1,
                    'storyNotFound': 1,
                    'hasMissingStory': 1,
                    'ageVerification': 1,
                    'redirectedFrom': 1,
                    'redirectedTo': 1}
    db.chapters.update_many({}, {'$unset': unset_fields})

    print('Done!\n')

    # REVIEWS
    print('Processing reviews...')

    # remove unused fields
    unset_fields = {'parentReviewableType': 1,
                    'parentReviewableUrl': 1,
                    'parentReviewedAt': 1,
                    'chapterNumber': 1,
                    'storyUrl': 1}
    db.reviews.update_many({}, {'$unset': unset_fields})

    # drop all indexes
    db.reviews.drop_indexes()

    print('Done!\n')

    # USERS
    print('Processing users...')

    # copy users to new table
    db.temp_users.drop()
    db.users.aggregate([{'$match': {}}, {'$out': 'temp_users'}])

    # set association fields
    # - source
    user_sources = db.temp_users.aggregate([{'$group': {'_id': "$sourceId"}}])
    for user_source in user_sources:
        source = db.sources.find_one({'_id': user_source['_id']})
        if source:
            db.temp_users.update_many({'sourceId': source['_id']}, {'$set': {'source': source['name']}})

    # remove unused fields
    unset_fields = {'isPreliminary': 1,
                    'setUsername': 1,
                    'notFound': 1}
    db.temp_users.update_many({}, {'$unset': unset_fields})

    print('Done!\n')

    # DATABASE CLEANUP
    print('Cleaning up database...')

    # - drop unused collections
    all_collections = db.list_collection_names()
    keep_collections = ['temp_stories', 'chapters', 'reviews', 'temp_users']
    drop_collections = [i for i in all_collections if i not in keep_collections]
    for collection in drop_collections:
        db[collection].drop()

    # - rename collections
    db.temp_stories.rename('stories', dropTarget=True)
    db.temp_users.rename('users', dropTarget=True)

    # - index collections
    story_indexes = [IndexModel([('authorId', ASCENDING)]),
                     IndexModel([('iid', ASCENDING)]),
                     IndexModel([('category', ASCENDING)]),
                     IndexModel([('fandoms', ASCENDING)]),
                     IndexModel([('genre', ASCENDING)]),
                     IndexModel([('pairings', ASCENDING)]),
                     IndexModel([('ratings', ASCENDING)]),
                     IndexModel([('source', ASCENDING)]),
                     IndexModel([('status', ASCENDING)]),
                     IndexModel([('tags', ASCENDING)]),
                     IndexModel([('topics', ASCENDING)]),
                     IndexModel([('characters', ASCENDING)]),
                     IndexModel([('numSentences', ASCENDING)]),
                     IndexModel([('numWords', ASCENDING)]),
                     IndexModel([('numLetters', ASCENDING)]),
                     IndexModel([('numCharacters', ASCENDING)])]
    db.stories.create_indexes(story_indexes)

    chapter_indexes = [IndexModel([('storyId', ASCENDING)]),
                       IndexModel([('numSentences', ASCENDING)]),
                       IndexModel([('numWords', ASCENDING)]),
                       IndexModel([('numLetters', ASCENDING)]),
                       IndexModel([('numCharacters', ASCENDING)])]
    db.chapters.create_indexes(chapter_indexes)

    review_indexes = [IndexModel([('parentId', ASCENDING)]),
                      IndexModel([('reviewableId', ASCENDING), ('reviewableType', ASCENDING)]),
                      IndexModel([('userId', ASCENDING)])]
    db.reviews.create_indexes(review_indexes)

    user_indexes = [IndexModel([('age', ASCENDING)]),
                    IndexModel([('country', ASCENDING)]),
                    IndexModel([('locatedAt', ASCENDING)]),
                    IndexModel([('source', ASCENDING)]),
                    IndexModel([('gender', ASCENDING)])]
    db.users.create_indexes(user_indexes)

    print('Done!')
finally:
    client.disconnect()
