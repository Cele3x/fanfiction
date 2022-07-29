#!/usr/bin/python3

import db_connect
from tqdm import tqdm

db = db_connect.db()

reviews = db['reviews'].find({'url': None, 'parentId': {'$ne': None}})
updated = 0
no_parent_url = 0
no_parent = 0
review_count = db['reviews'].count_documents({'url': None, 'parentId': {'$ne': None}})
with tqdm(total=review_count) as pbar:
    for review in reviews:
        pbar.update(1)
        if review['parentId']:
            parent = db['reviews'].find_one({'_id': review['parentId']})
            if 'url' in parent and parent['url']:
                db['reviews'].update_one({'_id': review['_id']}, {'$set': {'url': parent['url']}})
                updated += 1
            else:
                no_parent_url += 1
        else:
            no_parent += 1

print('Updated: ' + str(updated))
print('No parent: ' + str(no_parent))
print('No parent url: ' + str(no_parent_url))

db_connect.disconnect()
