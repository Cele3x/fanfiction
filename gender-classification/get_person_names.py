# -----------------------------------------------------------
# Generate a list containing all unique person names from
# the corpus.
# -----------------------------------------------------------

import csv
from datetime import datetime
from tqdm import tqdm
from utils.db_connect import DatabaseConnection


if __name__ == '__main__':
    print('%s - Start processing...' % '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
    client = DatabaseConnection()

    db = client.connect('FanFiction')
    if db is None:
        raise Exception('Database connection failed.')
    try:
        persons = set()

        with client.start_session() as session:
            query = {'isTagged': True, 'persons': {'$exists': True}}
            stories = db.stories.find(query, {'persons': 1}, session=session, no_cursor_timeout=True)
            story_count = db.stories.count_documents(query)
            with tqdm(total=story_count) as pbar:
                for story in stories:
                    for person in story['persons']:
                        persons.add(person)
                    pbar.update(1)

        print('Writing %i names to file...' % len(persons))
        with open('data/character_names.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['name', 'gender', 'probability'])
            for person in sorted(persons):
                writer.writerow([person, '', 0.0])

    except Exception as e:
        print(e)
    finally:
        client.disconnect()
