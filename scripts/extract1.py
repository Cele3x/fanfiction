#!/usr/bin/python3

import tarfile
import os
import csv
import multiprocessing as mp

INPUT_PATH = '/Volumes/Extern/fanfiction/stories/'
OUTPUT_PATH = '/Volumes/Extern/fanfiction/htmls/stories8/'
DONE_CSV = '/Volumes/Extern/fanfiction/out.csv'


def get_extracted_archives():
    data = []
    with open(DONE_CSV, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row[0])
            # data = list(reader)
    return data


def extract_archive(archive_path):
    print('Extracting ' + archive_path)
    with tarfile.open(archive_path, 'r:gz') as f:
        f.extractall(OUTPUT_PATH)
    with open(DONE_CSV, 'a') as fd:
        fd.writerow(archive_path)


def fanout_unziptar(path):
    """create pool to extract all"""
    done_archives = get_extracted_archives()
    open_archives = []
    for root, dirs, files in os.walk(path):
        for i in files:
            if i.endswith("tar.gz") and os.path.join(root, i) not in done_archives:
                open_archives.append(os.path.join(root, i))
    archives_count = len(open_archives)
    pool = mp.Pool(min(mp.cpu_count(), archives_count))  # number of workers
    pool.map(extract_archive, open_archives, chunksize=1)
    pool.close()


if __name__ == "__main__":
    print(f'CPUs: {mp.cpu_count()}')
    fanout_unziptar(INPUT_PATH)
    print(f'tar.gz extraction has completed')
