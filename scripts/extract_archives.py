#!/usr/bin/python3

# -----------------------------------------------------------
# Walks through specified directories containing
# tar.gz-archives and extracts them while storing the file
# and content information to the database.
# -----------------------------------------------------------

import tarfile
import os
import shutil
from db_connect import DatabaseConnection

INPUT_ARCHIVE_PATH_USERS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-users-20220222_books/'
OUTPUT_PATH_USERS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-users/'

INPUT_ARCHIVE_PATH_STORIES = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-stories-20220222_books/'
OUTPUT_PATH_STORIES = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-stories/'

INPUT_ARCHIVE_PATH_REVIEWS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-reviews-20220222_books/'
OUTPUT_PATH_REVIEWS = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-books-extracted-reviews/'

client = DatabaseConnection()
db = client.connect('FanfictionDB')

try:
    # extract archives with user html pages and store in csv_users collection
    for root, dirs, archives in os.walk(INPUT_ARCHIVE_PATH_USERS):
        for archive in archives:
            filepath = os.path.join(root, archive)
            if archive.endswith("tar.gz"):
                archive_name = os.path.basename(filepath)
                datestamp = archive_name.split('_', 1)[0][0:10]
                output_path = OUTPUT_PATH_USERS + datestamp + '/'
                print('Extracting ' + filepath + ' to ' + output_path)
                with tarfile.open(filepath, 'r:gz') as f:
                    filenames = [name for name in f.getnames() if name.endswith('.html')]
                    f.extractall(output_path)
                    for filename in filenames:
                        parts = filename.split('.')
                        uid = parts[0]  # e.g.: -BabyDoll-.html
                        url = 'https://www.fanfiktion.de/u/' + uid
                        csv_user = db['csv_users'].find_one({'filename': filename})
                        if not csv_user:
                            db['csv_users'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp})

    # extract archives with story html pages and store in csv_stories collection
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
                        parts = filename.split('_')  # e.g.: 4a298d450000e42606702328_4_Der-Alltag-eines-Genies.html
                        uid = parts[0]
                        chapter = parts[1]
                        title = parts[2].split('.')[0]
                        url = 'https://www.fanfiktion.de/s/' + uid + '/' + chapter + '/' + title
                        csv_story = db['csv_stories'].find_one({'filename': filename})
                        if not csv_story:
                            db['csv_stories'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp, 'chapter': chapter, 'title': title})

    # extract archives with review html pages and store in csv_reviews collection
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
                        parts = filename.split('_')  # e.g.: 4f36ea8000016c470670b798_date_0_4.html
                        uid = parts[0]
                        sorted_by = parts[1]
                        chapter = parts[2]
                        page = parts[3].split('.')[0]
                        url = 'https://www.fanfiktion.de/r/s/' + uid + '/' + sorted_by + '/' + chapter + '/' + page
                        csv_reviews = db['csv_reviews'].find_one({'filename': filename})
                        if not csv_reviews:
                            db['csv_reviews'].insert_one({'done': False, 'filename': filename, 'uid': uid, 'url': url, 'extracted_folder': datestamp, 'page': page})

finally:
    client.disconnect()
