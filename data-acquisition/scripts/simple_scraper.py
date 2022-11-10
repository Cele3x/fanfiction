#!/usr/bin/python3

# -----------------------------------------------------------
# Simple scraper using BeautifulSoup for filling smaller
# data gaps in previously crawled data.
# -----------------------------------------------------------

from bs4 import BeautifulSoup
from datetime import datetime
from utils.db_connect import DatabaseConnection
from time import sleep
from w3lib.html import replace_escape_chars
import re
import requests

if __name__ == "__main__":
    client = DatabaseConnection()
    try:
        db = client.connect('FanFiction')
        if db is None:
            raise Exception('Database connection failed.')

        chapters = db.chapters.find({'url': {'$regex': r'https:\/\/archiveofourown'}, 'numCharacters': {'$lte': 100}})
        for chapter in chapters:
            print('URL: %s' % chapter['url'])

            page = requests.get(chapter['url'])
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                item = soup.select('div#chapters div.userstuff')[0]
                header = item.find('h3', id='work')
                if header:
                    header.decompose()
                item_clean = item.getText(separator='\n')
                item_clean = replace_escape_chars(item_clean, which_ones=('\t', '\r'), replace_by=' ')
                item_clean = re.sub(r'(\n\s?)+', '\n', item_clean)
                item_clean = item_clean.replace(u'\xa0', u' ')
                item_clean = re.sub(r' +', ' ', item_clean)
                item_clean = item_clean.strip()
                print(item_clean)
                sleep(7)
                db.chapters.update_one({'_id': chapter['_id']}, {'$set': {'content': item_clean, 'numCharacters': None, 'numSentences': None, 'updatedAt': datetime.now()}})
            else:
                print('Status code: %s' % page.status_code)
                sleep(7)

    except Exception as e:
        print(e)
    finally:
        client.disconnect()
