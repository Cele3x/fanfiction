#!/usr/bin/python3

# -----------------------------------------------------------
# Extracts archives for storing them in a new archive
# consisting of 1,000 files.
# -----------------------------------------------------------

import os
import tarfile
from glob import glob
from datetime import datetime


def archive_files(item_type: str) -> None:
    file_count = 0
    archive_count = 0
    output_path = 'temp/'
    for archive in glob('../pages/' + item_type + '/*.tar.gz'):
        archive_count += 1
        with tarfile.open(archive) as f:
            names = [name for name in f.getnames() if name.endswith('.html')]
            file_count += len(names)
            f.extractall(output_path)
        if file_count >= 1000:
            filelist = [os.path.join(output_path, file) for file in os.listdir(output_path) if file.endswith('.html')]
            archive_name = output_path + datetime.now().strftime("%Y%m%d%H%M%S%f") + '_' + item_type + '.tar.gz'
            with tarfile.open(archive_name, "w:gz") as f:
                for file in filelist:
                    f.add(file)  # add to archive
                    os.remove(file)  # delete file
            print('Archive', archive_count, ':', archive_name)
            file_count = 0
    filelist = [os.path.join(output_path, file) for file in os.listdir(output_path) if file.endswith('.html')]
    archive_name = output_path + datetime.now().strftime("%Y%m%d%H%M%S%f") + '_' + item_type + '.tar.gz'
    with tarfile.open(archive_name, "w:gz") as f:
        for file in filelist:
            f.add(file, arcname=file.split('/')[-1])  # add to archive
            os.remove(file)  # delete file
    print('Archive:', archive_name)


archive_files('users')
archive_files('stories')
archive_files('reviews')
