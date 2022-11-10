# -----------------------------------------------------------
# Cleanses the tagged character names in the database.
# -----------------------------------------------------------

import re
import time
from datetime import datetime
from pymongo import UpdateOne
from tqdm import tqdm
from unidecode import unidecode
from utils.db_connect import DatabaseConnection

UMLAUTS = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('Ä'): 'Ae', ord('Ü'): 'Ue', ord('Ö'): 'Oe'}


if __name__ == '__main__':
    client = DatabaseConnection()
    try:
        print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))

        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        with client.start_session() as session:

            # find tagged persons
            chapter_query = {'isTagged': True}
            chapters = db.chapters.find(chapter_query, session=session, no_cursor_timeout=True)
            num_chapters = db.chapters.count_documents(chapter_query)

            # initialize update containers
            db_chapter_updates = []

            with tqdm(total=num_chapters) as pbar:
                for index, chapter in enumerate(chapters):
                    pbar.set_description('Processing chapter %s...' % (chapter['_id']))

                    # initialize cleansed persons container
                    cleansed_names = {}

                    for name, occurrences in chapter['persons'].items():
                        # print('Processing name "%s"...' % name, end=' ', flush=True)

                        # lowercase name
                        cleansed_name = name.lower()

                        # translate umlauts
                        cleansed_name = cleansed_name.translate(UMLAUTS)

                        # unidecode name
                        cleansed_name = unidecode(cleansed_name)

                        # remove genitive apostrophe
                        cleansed_name = re.sub(r'\'s', '', cleansed_name)

                        # remove all non-alphanumeric characters except spaces and dashes
                        cleansed_name = re.sub(r'[^\w\s-]', ' ', cleansed_name)

                        # remove duplicate spaces
                        cleansed_name = re.sub(r'\s+', ' ', cleansed_name)

                        # remove all leading and trailing whitespace
                        cleansed_name = cleansed_name.strip()

                        # print('> "%s"' % cleansed_name)

                        # check if name is already in cleansed names and cumulate occurrences
                        if cleansed_name in cleansed_names:
                            cleansed_names[cleansed_name] += occurrences
                        else:
                            cleansed_names[cleansed_name] = occurrences

                    db_chapter_updates.append(UpdateOne({'_id': chapter['_id']}, {'$set': {'cleansedNames': cleansed_names}}))

                    # refresh every 50000 chapters the session and bulk write the chapter updates
                    if index % 50000 == 0:
                        client.refresh_session(session.session_id)

                        # bulk write chapter updates
                        if db_chapter_updates:
                            print('\n%s - Updating %d chapters...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_chapter_updates)))
                            db.chapters.bulk_write(db_chapter_updates)
                            db_chapter_updates = []

                    pbar.update(1)

            print('\n%s - Updating %d chapters...' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), len(db_chapter_updates)))
            db.chapters.bulk_write(db_chapter_updates)
    except Exception as e:
        print(e)
    finally:
        client.disconnect()
