#!/usr/bin/python3

import tarfile
import os
import csv
import shutil
import pymongo
from dotenv import load_dotenv
import urllib.parse

load_dotenv('../.env')

MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)

INPUT_ARCHIVE_PATH_USERS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-users-20220222_books/'
OUTPUT_PATH_USERS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-users/'

INPUT_ARCHIVE_PATH_STORIES = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-stories-20220222_books/'
OUTPUT_PATH_STORIES = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-stories/'

INPUT_ARCHIVE_PATH_REVIEWS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-reviews-20220222_books/'
OUTPUT_PATH_REVIEWS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-reviews/'

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

# for root, dirs, archives in os.walk(INPUT_ARCHIVE_PATH_USERS):
#     for archive in archives:
#         filepath = os.path.join(root, archive)
#         if archive.endswith("tar.gz"):
#             archive_name = os.path.basename(filepath)
#             datestamp = archive_name.split('_', 1)[0][0:10]
#             output_path = OUTPUT_PATH_USERS + datestamp + '/'
#             print('Extracting ' + filepath + ' to ' + output_path)
#             with tarfile.open(filepath, 'r:gz') as f:
#                 filenames = [name for name in f.getnames() if name.endswith('.html')]
#                 f.extractall(output_path)
#                 for filename in filenames:
#                     parts = filename.split('.')
#                     uid = parts[0]  # -BabyDoll-.html
#                     url = 'https://www.fanfiktion.de/u/' + uid
#                     csv_user = db['csv_users'].find_one({'filename': filename})
#                     if not csv_user:
#                         db['csv_users'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp})

for root, dirs, archives in os.walk(INPUT_ARCHIVE_PATH_STORIES):
    num = 0
    idx = 0
    for archive in archives:
        idx += 1
        if idx % 7 == 0:
            num += 1
        filepath = os.path.join(root, archive)
        if archive.endswith("tar.gz"):
            archive_name = os.path.basename(filepath)
            datestamp = archive_name.split('_', 1)[0][0:8]
            output_path = OUTPUT_PATH_STORIES + datestamp + str(num) + '/'
            print('Extracting ' + filepath + ' to ' + output_path)
            with tarfile.open(filepath, 'r:gz') as f:
                filenames = [name.replace('temp/', '') for name in f.getnames() if name.endswith('.html')]
                f.extractall(output_path)
                temp_files = os.listdir(output_path + 'temp/')
                for temp_file in temp_files:
                    temp_file_name = os.path.join(output_path + 'temp/', temp_file)
                    if not os.path.exists(output_path + temp_file):
                        shutil.move(temp_file_name, output_path)
                for filename in filenames:
                    parts = filename.split('_')  # 4a298d450000e42606702328_4_Der-Alltag-eines-Genies.html
                    uid = parts[0]
                    chapter = parts[1]
                    title = parts[2].split('.')[0]
                    url = 'https://www.fanfiktion.de/s/' + uid + '/' + chapter + '/' + title
                    csv_story = db['csv_stories'].find_one({'filename': filename})
                    if not csv_story:
                        db['csv_stories'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp, 'chapter': chapter, 'title': title})

for root, dirs, archives in os.walk(INPUT_ARCHIVE_PATH_REVIEWS):
    num = 0
    idx = 0
    for archive in archives:
        idx += 1
        if idx % 7 == 0:
            num += 1
        filepath = os.path.join(root, archive)
        if archive.endswith("tar.gz"):
            archive_name = os.path.basename(filepath)
            datestamp = archive_name.split('_', 1)[0][0:8]
            output_path = OUTPUT_PATH_REVIEWS + datestamp + str(num) + '/'
            print('Extracting ' + filepath + ' to ' + output_path)
            with tarfile.open(filepath, 'r:gz') as f:
                filenames = [name.replace('temp/', '') for name in f.getnames() if name.endswith('.html')]
                f.extractall(output_path)
                temp_files = os.listdir(output_path + 'temp/')
                for temp_file in temp_files:
                    temp_file_name = os.path.join(output_path + 'temp/', temp_file)
                    if not os.path.exists(output_path + temp_file):
                        shutil.move(temp_file_name, output_path)
                for filename in filenames:
                    parts = filename.split('_')  # 4f36ea8000016c470670b798_date_0_4.html
                    uid = parts[0]
                    sorted_by = parts[1]
                    chapter = parts[2]
                    page = parts[3].split('.')[0]
                    url = 'https://www.fanfiktion.de/r/s/' + uid + '/' + sorted_by + '/' + chapter + '/' + page
                    csv_reviews = db['csv_reviews'].find_one({'filename': filename})
                    if not csv_reviews:
                        db['csv_reviews'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp, 'page': page})

client.close()
