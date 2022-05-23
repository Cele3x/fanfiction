import re
import os
import csv
from fanfiction.settings import MONGO_URI, MONGO_DB, EXTRACTED_STORIES_PATH, EXTRACTED_USERS_PATH, EXTRACTED_REVIEWS_PATH, CSV_STORIES_PATH, CSV_USERS_PATH, CSV_REVIEWS_PATH
from pymongo import MongoClient
from abc import ABC
from fanfiction.utilities import get_datetime, get_date, str_to_int
from tqdm import tqdm

from scrapy.http import Request
from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from scrapy.spiders import CrawlSpider

from w3lib.html import replace_tags, replace_escape_chars

from fanfiction.items import Story, Chapter, User, Review


def find_story_definitions(text: str) -> list:
    """Find story definitions inside HTML snippet.
    e.g. '<div class="small-font center block">\nGeschichte<span class="fas fa-angle-right" style="margin:0 .4em;"></span>Schmerz/Trost, Suspense / P16 / Gen\n</div>'

    :param text: str
        with HTML elements containing tags and excape chars
    :return: list
        with elements split by ' / ' character
    """
    text = replace_escape_chars(text)
    text = replace_tags(text, ' / ')
    return list(filter(None, [x.strip() for x in text.split(' / ')]))


class FanfiktionHtmlExtractSpider(CrawlSpider, ABC):
    name = 'FanFiktionHtmlExtract'

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': 'False',
        'AUTOTHROTTLE_ENABLED': 'False',
        'ITEM_PIPELINES': {
            'fanfiction.pipelines.FanfictionHtmlPipeline': 400
        }
    }

    def start_requests(self):
        # iterative [#1] -> user
        # for csv_user in self.db['csv_users'].find({'done': False}):
        #     filepath = os.path.join(EXTRACTED_USERS_PATH, csv_user['extracted_folder'], csv_user['filename'])
        #     if os.path.isfile(filepath):
        #         yield Request(url='file://' + filepath, callback=self.parse_user, cb_kwargs=dict(csv_user=csv_user))
        # iterative [#2] -> stories with chapter = 1
        # for csv_story in self.db['csv_stories'].find({'done': False, 'chapter': '1', 'extracted_folder': {'$ne': None}}):
        #     filepath = os.path.join(EXTRACTED_STORIES_PATH, csv_story['extracted_folder'], csv_story['filename'])
        #     if os.path.isfile(filepath):
        #         yield Request(url='file://' + filepath, callback=self.parse_story, cb_kwargs=dict(csv_story=csv_story))
        # iterative [#3] -> chapters != 1
        # for csv_chapter in self.db['csv_stories'].find({'done': False, 'chapter': {'$ne': '1'}}):
        #     filepath = os.path.join(EXTRACTED_STORIES_PATH, csv_chapter['extracted_folder'], csv_chapter['filename'])
        #     if os.path.isfile(filepath):
        #         csv_story = self.db['csv_stories'].find_one({'chapter': '1', 'uid': csv_chapter['uid']})
        #         yield Request(url='file://' + filepath, callback=self.parse_chapter, cb_kwargs=dict(csv_story=csv_story, csv_chapter=csv_chapter))
        # iterative [#4] -> reviews
        for csv_reviews in self.db['csv_reviews'].find({'done': False}):
            if 'extracted_folder' in csv_reviews:
                filepath = os.path.join(EXTRACTED_REVIEWS_PATH, csv_reviews['extracted_folder'], csv_reviews['filename'])
            else:
                filepath = os.path.join(EXTRACTED_REVIEWS_PATH, csv_reviews['filename'])
            if os.path.isfile(filepath):
                csv_story = self.db['csv_story'].find_one({'chapter': '1', 'uid': csv_reviews['uid']})
                yield Request(url='file://' + filepath, callback=self.parse_reviews, cb_kwargs=dict(csv_story=csv_story, csv_reviews=csv_reviews))

    def __init__(self, *a, **kw):
        super(FanfiktionHtmlExtractSpider, self).__init__(*a, **kw)
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FanfiktionHtmlExtractSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.handle_spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.handle_spider_closed, signals.spider_closed)
        return spider

    def handle_spider_opened(self, spider):
        spider.logger.info('Spider opened: %s', spider.name)
        # if not os.path.isdir(EXTRACTED_STORIES_PATH) or not os.path.isdir(EXTRACTED_USERS_PATH) or not os.path.isdir(EXTRACTED_REVIEWS_PATH):
        #     spider.logger.info('Specified extracted paths from .env-file are no valid directories')
        #     raise CloseSpider
        # if not os.path.isfile(CSV_STORIES_PATH) or not os.path.isfile(CSV_USERS_PATH) or not os.path.isfile(CSV_REVIEWS_PATH):
        #     spider.logger.info('Specified CSV files from .env-file are no valid')
        #     raise CloseSpider
        # self.store_csvs()

    def handle_spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)
        self.client.close()

    def store_csvs(self):
        if os.path.isfile(CSV_STORIES_PATH):
            print('Storing stories from CSV file into database...')
            with open(CSV_STORIES_PATH) as f:
                reader = csv.reader(f, delimiter=',')
                for row in tqdm(reader):
                    csv_story = self.db['csv_stories'].find_one({'url': row[1]})
                    if not csv_story:
                        self.db['csv_stories'].insert_one({'filename': row[0], 'url': row[1], 'uid': row[2], 'title': row[3], 'chapter': row[4], 'done': False})
        if os.path.isfile(CSV_USERS_PATH):
            print('Storing users from CSV file into database...')
            with open(CSV_USERS_PATH) as f:
                reader = csv.reader(f, delimiter=',')
                for row in tqdm(reader):
                    csv_user = self.db['csv_users'].find_one({'url': row[1]})
                    if not csv_user:
                        self.db['csv_users'].insert_one({'filename': row[0], 'url': row[1], 'uid': row[2], 'done': False})
        if os.path.isfile(CSV_REVIEWS_PATH):
            print('Storing reviews from CSV file into database...')
            with open(CSV_REVIEWS_PATH) as f:
                reader = csv.reader(f, delimiter=',')
                for row in tqdm(reader):
                    csv_reviews = self.db['csv_reviews'].find_one({'url': row[1]})
                    if not csv_reviews:
                        self.db['csv_reviews'].insert_one({'filename': row[0], 'url': row[1], 'uid': row[2], 'page': row[3], 'done': False})

    def parse_story(self, response, csv_story):
        """Parses story item."""
        loader = ItemLoader(item=Story(), selector=response)

        # mark stories with age verification
        if response.css('div#content > div.pageviewframe').xpath('.//div[contains(., "Meldung")]'):
            loader.add_value('ageVerification', True)

        # general data
        loader.add_value('source', 'FanFiktion')
        story_path = response.css('#ffcbox-story-topic-1 a::text').getall()
        if story_path:
            loader.add_value('genre', story_path[1])
            loader.add_value('fandoms', story_path[2:-1])

        # left side data
        left = loader.nested_css('div.story-left')
        left_sel = response.css('div.story-left')

        if not left_sel:
            left = loader
            left_sel = response
        left.add_css('title', 'h4.huge-font')
        summary_text = response.css('div#story-summary-inline *::text').get()
        if summary_text:
            if summary_text == '(Der Autor hat keine Kurzbeschreibung zu dieser Geschichte verfasst.)':
                summary_text = None
            left.add_value('summary', summary_text)
        story_definitions_block = left_sel.css('div.small-font.center.block')
        if story_definitions_block:
            definitions = find_story_definitions(story_definitions_block.get())
            left.add_value('category', definitions[0])
            left.add_value('topics', definitions[1])
            left.add_value('rating', definitions[2])
            left.add_value('pairing', definitions[3])
        if left_sel.xpath('.//span[contains(@title, "Fertiggestellt")]'):
            left.add_value('status', 'done')
        elif left_sel.xpath('.//span[contains(@title, "in Arbeit")]'):
            left.add_value('status', 'work in progress')
        elif left_sel.xpath('.//span[contains(@title, "Pausiert")]'):
            left.add_value('status', 'paused')
        elif left_sel.xpath('.//span[contains(@title, "Abgebrochen")]'):
            left.add_value('status', 'cancelled')
        left.add_xpath('likes', './/span[contains(@title, "Empfehlungen")]/../text()')
        left.add_css('characters', 'span.badge-character')
        user_url_trail = left_sel.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
        if user_url_trail:
            user_url = 'https://www.fanfiktion.de' + user_url_trail
            left.add_value('authorUrl', user_url)
        left.add_value('url', csv_story['url'])
        published_on = left_sel.xpath('.//span[contains(@title, "erstellt")]/../text()').getall()
        if published_on:
            left.add_value('publishedOn', get_date(''.join(published_on)))
        reviewed_on = left_sel.xpath('.//span[contains(@title, "aktualisiert")]/../text()').getall()
        if reviewed_on:
            left.add_value('reviewedOn', get_date(''.join(reviewed_on)))
        total_chapter_count = left_sel.xpath('.//span[contains(@title, "Kapitel")]/..').css('span.semibold::text').get()
        if total_chapter_count:
            left.add_value('totalChapterCount', total_chapter_count)

        yield loader.load_item()
        yield from self.parse_chapter(response, csv_story, csv_story)

    def parse_chapter(self, response, csv_story, csv_chapter):
        """Parses chapters and following."""
        if not csv_story:
            return False

        right_sel = response.css('div.story-right')
        loader = ItemLoader(item=Chapter(), selector=right_sel)
        loader.add_value('storyUrl', csv_story['url'])
        loader.add_value('url', csv_chapter['url'])
        loader.add_css('content', 'div#storytext')
        published_on = right_sel.xpath('.//span[contains(@title, "Kapitel erstellt am")]/../text()').get()
        if published_on:
            loader.add_value('publishedOn', get_date(''.join(published_on)))
        chapter_number = right_sel.xpath('.//select[@id="kA"]/option[contains(@selected, "selected")]/@value').get()
        loader.add_value('number', chapter_number)
        chapter_title = right_sel.xpath('.//select[@id="kA"]/option[contains(@selected, "selected")]/text()').get()
        if chapter_title:
            chapter_title = re.sub(r'^\d+\.\s?', '', chapter_title)  # remove title numbering
            loader.add_value('title', chapter_title)
        yield loader.load_item()

    def parse_user(self, response, csv_user):
        """Parses user item."""

        loader = ItemLoader(item=User(), selector=response)

        # general data
        loader.add_value('source', 'FanFiktion')
        loader.add_css('username', 'div.userprofile-bio-table-outer h2')

        self.db['csv_users'].find_one({})
        loader.add_value('url', csv_user['url'])

        bio_table = loader.nested_css('div.userprofile-bio-table')
        bio_table_sel = response.css('div.userprofile-bio-table')
        bio_table.add_xpath('firstName', './/div[contains(text(), "Vorname:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('lastName', './/div[contains(text(), "Nachname:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('locatedAt', './/div[contains(text(), "Wohnort:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('country', './/div[contains(text(), "Land:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        gender = bio_table_sel.xpath('.//div[contains(text(), "Geschlecht:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()').get()
        if gender == 'männlich':
            bio_table.add_value('gender', 'male')
        elif gender == 'weiblich':
            bio_table.add_value('gender', 'female')
        elif gender == 'divers':
            bio_table.add_value('gender', 'other')
        bio_table.add_xpath('age', './/div[contains(text(), "Alter:")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')

        story_related = loader.nested_css('div#ffcbox-stories')
        if response.css('div#ffcbox-stories-layer-aboutme div.status-message').xpath('.//div[contains(text(), "Dieser Benutzer hat keine Informationen über sich veröffentlicht.")]'):
            story_related.add_value('bio', None)
        else:
            story_related.add_css('bio', 'div#ffcbox-stories-layer-aboutme')

        yield loader.load_item()

    def parse_reviews(self, response, csv_story, csv_reviews):
        """Parses review items."""
        if not csv_story:
            return False

        for review in response.css('div.review'):
            loader = ItemLoader(item=Review(), selector=review)
            loader.add_value('url', csv_reviews['url'])

            # left side data
            left = loader.nested_css('div.review-left')
            left_sel = review.css('div.review-left')
            user_url = left_sel.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
            if user_url:
                left.add_value('userUrl', 'https://www.fanfiktion.de' + user_url)
            reviewed_at = left_sel.xpath('.//div[contains(text(), "Uhr")]/text()').get()
            if reviewed_at:
                left.add_value('reviewedAt', get_datetime(reviewed_at))
            if left_sel.xpath('.//i[contains(text(), "Kapitel")]'):  # review for Chapter
                reviewable_type = 'Chapter'
                left.add_value('reviewableType', reviewable_type)
                reviewable_url = left_sel.xpath('.//a[starts-with(@href, "/s/")]/@href').get()
                if reviewable_url:
                    left.add_value('reviewableUrl', 'https://www.fanfiktion.de' + reviewable_url)
            else:  # review for Story
                reviewable_type = 'Story'
                left.add_value('reviewableType', reviewable_type)
                reviewable_url = csv_story['url']
                left.add_value('reviewableUrl', reviewable_url)

            # right side data
            right = loader.nested_css('div.review-right')
            right_sel = review.css('div.review-right')
            right.add_css('content', 'div.user-formatted-inner > span.usercontent')

            # there is just ONE reply possible and only from the author of the reviewed story
            reply = right_sel.css('div.review-reply')
            if reply:
                reply_loader = ItemLoader(item=Review(), selector=reply)
                reply_user_url = reply.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
                if reply_user_url:
                    reply_loader.add_value('userUrl', 'https://www.fanfiktion.de' + reply_user_url)
                reply_reviewed_at = reply.css('div.bold.padded-vertical *::text').getall()[-1]
                if reply_reviewed_at:
                    reply_loader.add_value('reviewedAt', get_datetime(reply_reviewed_at))
                reply_loader.add_css('content', 'span.usercontent')
                if reviewable_type:
                    reply_loader.add_value('reviewableType', reviewable_type)
                    reply_loader.add_value('parentReviewableType', reviewable_type)
                if reviewable_url:
                    reply_loader.add_value('reviewableUrl', 'https://www.fanfiktion.de' + reviewable_url)
                    reply_loader.add_value('parentReviewableUrl', 'https://www.fanfiktion.de' + reviewable_url)
                if user_url:
                    reply_loader.add_value('parentUserUrl', 'https://www.fanfiktion.de' + user_url)
                if reviewed_at:
                    reply_loader.add_value('parentReviewedAt', get_datetime(reviewed_at))
                yield reply_loader.load_item()

            yield loader.load_item()
