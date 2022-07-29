#!/usr/bin/python3

import tarfile
import os
import csv

# INPUT_PATH = '/Volumes/Extern/fanfiction/stories/'
INPUT_PATH = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-reviews-20220222_books/'
OUTPUT_PATH = '/Users/jonathan/Documents/Studium/Master/Masterarbeit/data/html-reviews-extracted_books/'
# OUTPUT_PATH = '/Volumes/Extern/fanfiction/htmls2/stories/'
DONE_CSV_PATH = 'result_reviews.csv'


done_archives = []
with open(DONE_CSV_PATH, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        done_archives.append(row[0])

open_archives = []
for root, dirs, files in os.walk(INPUT_PATH):
    for file in files:
        filepath = os.path.join(root, file)
        if file.endswith("tar.gz") and filepath not in done_archives:
            open_archives.append(filepath)

for archive in open_archives:
    filename = os.path.basename(archive)
    datestamp = filename.split('_', 1)[0][0:8]
    output_path = OUTPUT_PATH + '/' + datestamp + '/'
    print('Extracting ' + archive + ' to ' + output_path)
    with tarfile.open(archive, 'r:gz') as f:
        f.extractall(output_path)
    with open(DONE_CSV_PATH, 'a') as fd:
        writer = csv.writer(fd)
        extracted_folder = datestamp
        writer.writerow([filename, archive, output_path, extracted_folder])
