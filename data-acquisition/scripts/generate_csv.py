#!/usr/bin/python3

# -----------------------------------------------------------
# Extracts filenames from archives files and derives urls
# from them. The gathered information are being stored in
# csv-files for stories, users and reviews accordingly.
# -----------------------------------------------------------

from glob import glob
import tarfile
import csv

stories = set()
for file in glob('../pages/stories/*.gz'):
    t = tarfile.open(file)
    names = [name for name in t.getnames() if name.endswith('.html')]
    print(file + ': ' + str(len(names)))
    stories.update(names)

users = set()
for file in glob('../pages/users/*.gz'):
    t = tarfile.open(file)
    names = [name for name in t.getnames() if name.endswith('.html')]
    print(file + ': ' + str(len(names)))
    users.update(names)

reviews = set()
for file in glob('../pages/reviews/*.gz'):
    t = tarfile.open(file)
    names = [name for name in t.getnames() if name.endswith('.html')]
    print(file + ': ' + str(len(names)))
    reviews.update(names)

print('Stories: ' + str(len(stories)))
print('Users: ' + str(len(users)))
print('Reviews: ' + str(len(reviews)))

with open('users.csv', 'a', encoding='UTF8') as f:
    writer = csv.writer(f)
    for user in sorted(users):
        parts = user.split('.')
        uid = parts[0]  # e.g.: -BabyDoll-.html
        url = 'https://www.fanfiktion.de/u/' + uid
        writer.writerow([user, url, uid])

uniq_stories = set()
with open('stories.csv', 'a', encoding='UTF8') as f:
    writer = csv.writer(f)
    for story in sorted(stories):
        parts = story.split('_')  # e.g.: 4a298d450000e42606702328_4_Der-Alltag-eines-Genies.html
        uid = parts[0]
        chapter = parts[1]
        title = parts[2].split('.')[0]
        url = 'https://www.fanfiktion.de/s/' + uid + '/' + chapter + '/' + title
        writer.writerow([story, url, uid, title, chapter])
        uniq_stories.add(uid)

with open('reviews.csv', 'a', encoding='UTF8') as f:
    writer = csv.writer(f)
    for review in sorted(reviews):
        parts = review.split('_')  # e.g.: 4f36ea8000016c470670b798_date_0_4.html
        uid = parts[0]
        sorted_by = parts[1]
        chapter = parts[2]
        page = parts[3].split('.')[0]
        url = 'https://www.fanfiktion.de/r/s/' + uid + '/' + sorted_by + '/' + chapter + '/' + page
        writer.writerow([review, url, uid, page])

print('Unique Stories: ' + str(len(uniq_stories)))
