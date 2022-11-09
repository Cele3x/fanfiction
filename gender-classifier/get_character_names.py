# -----------------------------------------------------------
# Generate a list containing all unique character names from the corpus.
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
        # df = pd.read_csv('data/character_names.csv')
        # df.head()

        names = set()

        with client.start_session() as session:
            chapter_count = db.chapters.count_documents({'isTagged': True})
            chapters = db.chapters.find({'isTagged': True}, {'persons': 1}, session=session, no_cursor_timeout=True)
            with tqdm(total=chapter_count) as pbar:
                for chapter in chapters:
                    for name in chapter['persons']:
                        if '~' not in name:
                            names.add(name)
                    pbar.update(1)

        print('Writing %i names to file...' % len(names))
        with open('data/character_names.csv', 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['name', 'gender'])
            for name in names:
                writer.writerow([name, ''])

    except Exception as e:
        print(e)
    finally:
        client.disconnect()
