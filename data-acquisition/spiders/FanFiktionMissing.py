import re
from datetime import datetime

from scrapy.spidermiddlewares.httperror import HttpError
from tqdm import tqdm

from scrapy.exceptions import CloseSpider

from ..settings import MONGO_URI, MONGO_DB
from pymongo import MongoClient
from bson.objectid import ObjectId
from abc import ABC
from ..utilities import get_datetime, get_date, str_to_int

from scrapy.http import Request
from scrapy import signals
from pydispatch import dispatcher
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from w3lib.html import replace_tags, replace_escape_chars

from ..items import Story, Chapter, User, Review


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


class FanfiktionSpider(CrawlSpider, ABC):
    name = 'FanFiktionMissing'
    download_delay = 0.725
    allowed_domains = ['fanfiktion.de']

    custom_settings = {
        # 'JOBDIR': 'crawls/FanFiktion-Missing',
    }

    def start_requests(self):
        users = self.db.users.find({'username': None, 'url': {'$regex': '^https:\/\/www\.fanfiktion\.de\/s'}})
        user_count = self.db.users.count_documents({'username': None, 'url': {'$regex': '^https:\/\/www\.fanfiktion\.de\/s'}})

        with tqdm(total=user_count) as pbar:
            for user in users:
                pbar.update(1)
                if 'url' in user:
                    yield Request(url=user['url'], callback=self.parse_user_from_story, cookies=self.auth_cookies, cb_kwargs=dict(user=user))

    def parse_user_from_story(self, response, user):
        left = response.css('div.story-left')
        user_sub_url = left.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
        if user_sub_url:
            user_url = response.urljoin(user_sub_url)
            correct_user = self.db.users.find_one({'url': user_url})
            if correct_user:
                self.db.stories.update_many({'authorId': user['_id']}, {'$set': {'authorId': correct_user['_id']}})
                self.db.users.delete_one({'_id': user['_id']})
            else:
                self.db.users.update_one({'_id': user['_id']}, {'$set': {'url': user_url}})
            yield Request(user_url, callback=self.parse_user)

    # def start_requests(self):
    #     items = self.db.chapters.find({'hasMissingContent': True})
    #     items_count = self.db.chapters.count_documents({'hasMissingContent': True})
    #
    #     with tqdm(total=items_count) as pbar:
    #         for item in items:
    #             pbar.update(1)
    #             if 'url' in item:
    #                 iid = item['url'].split('/')[4]
    #                 # iid = item['iid']
    #                 pbar.set_description('Processing ' + iid)
    #                 story = self.db.stories.find_one({'iid': iid})
    #                 # if story:
    #                 #     print('Using iid as Identifier - ' + iid)
    #                 #     self.db.stories.delete_one({'_id': item['_id'], 'title': None})
    #                 # else:
    #                 #     story_url = 'https://www.fanfiktion.de/s/' + iid
    #                 story_url = story['url']
    #                 yield Request(url=item['url'], callback=self.parse_chapter, cookies=self.auth_cookies, errback=self.handle_failed_request, cb_kwargs=dict(story_url=story_url))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.auth_cookies = []  # https://www.fanfiktion.de/?a=l
        self.auth_cookies = [
            {'name': 'i', 'value': '1f80c0f2352e815c831a199fd8e30d442ff5af6bba7d208765e6d6bb6305802bb912bb813dca1fcb3308605762cc9284e642dfaafb2bb3c65a989f1ccb78535e', 'domain': '.fanfiktion.de', 'path': '/'},
            {'name': 'l', 'value': '%22y~Y%22EK8v%2AJRmd8mA%228T', 'domain': '.fanfiktion.de', 'path': '/'},
            {'name': 's', 'value': '1', 'domain': '.fanfiktion.de', 'path': '/'},
            {'name': 'u', 'value': 'LzSjZ9KrMDBnnciV%7CWnHRuyshembsTrAQoHGTbWXwXCrHhbxXpyaow30g0Tc%3D', 'domain': '.fanfiktion.de', 'path': '/'},
        ]

    def spider_closed(self, spider):
        self.client.close()

    def handle_failed_request(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.db['stories'].update_one({'url': response.url}, {'$set': {'notFound': True}})
            self.db['chapters'].update_one({'url': response.url}, {'$set': {'notFound': True}})
            self.db['users'].update_one({'url': response.url}, {'$set': {'notFound': True}})
            self.logger.error('HttpError on %s', response.url)

    def parse_item(self, response):
        """Processes item by evaluating their type and passing it to the appropriate parser."""
        if response.status != 200:
            raise CloseSpider('Closing spider due to HTTP error')

        for item in response.css('div.storylist-item'):
            user_url = response.urljoin(item.xpath('.//a[starts-with(@href, "/u/")]/@href').get())
            story_url = response.urljoin(item.xpath('.//a[starts-with(@href, "/s/")]/@href').get())
            reviews_url = response.urljoin(item.xpath('.//a[starts-with(@href, "/r/s/")]/@href').get())
            total_review_count = item.xpath('.//a[starts-with(@href, "/r/s/")]/text()').get()
            if self.db['users'].find_one({'url': user_url, 'isPreliminary': False}) is None:
                yield Request(user_url, callback=self.parse_user)
            story = self.db['stories'].find_one({'url': story_url})
            review = self.db['reviews'].find_one({'url': reviews_url})
            has_missing_reviews = story and ('currentReviewCount' not in story or 'totalReviewCount' not in story or str_to_int(story['totalReviewCount']) == 0 or str_to_int(story['currentReviewCount']) < str_to_int(
                story['totalReviewCount']))
            if review is None or has_missing_reviews:
                yield Request(reviews_url, callback=self.parse_reviews, cb_kwargs=dict(story_url=story_url))
            has_missing_chapters = story and (
                    'currentChapterCount' not in story or 'totalChapterCount' not in story or str_to_int(story['totalChapterCount']) == 0 or str_to_int(story['currentChapterCount']) < str_to_int(
                story['totalChapterCount']))
            if story is None or has_missing_chapters:
                if has_missing_chapters:
                    self.logger.info('Story with missing chapters: {}'.format(story))
                yield Request(story_url, callback=self.parse_story, cb_kwargs=dict(user_url=user_url, total_review_count=total_review_count, story=story))
            else:
                self.logger.info('Story exists')

    def parse_fandom(self, response, story=None):
        self.logger.info('PARSING %s', response.url)
        story_path = response.css('#ffcbox-story-topic-1 a::text').getall()
        if story_path:
            f = ' - '.join(story_path[2:-1])
            fandom = self.db['fandoms'].find_one({'$or': [{'name1': f}, {'name2': f}, {'name3': f}]})
            if fandom is None:
                fandom = self.db['fandoms'].insert_one({'name1': f, 'createdAt': datetime.now(), 'updatedAt': datetime.now()})
                fandom_id = fandom.inserted_id
            else:
                fandom_id = fandom['_id']
            if fandom_id:
                if story and '_id' in story:
                    story_fandom = self.db['story_fandoms'].find_one({'storyId': story['_id'], 'fandomId': fandom_id})
                    if story_fandom is None:
                        self.logger.info('New StoryFandom with url %s', response.url)
                        self.db['story_fandoms'].insert_one({'storyId': story['_id'], 'fandomId': fandom_id, 'createdAt': datetime.now(), 'updatedAt': datetime.now()})

    def parse_story(self, response, user_url=None, total_review_count=None, story=None):
        """Parses story item."""

        if response.url == 'https://www.fanfiktion.de/?a=l':
            raise CloseSpider('Closing spider due to timed out session')

        loader = ItemLoader(item=Story(), selector=response)

        # mark stories with age verification
        if response.css('div#content > div.pageviewframe').xpath('.//div[contains(., "Meldung")]') or response.css('div#content > div.story > div.pageviewframe').xpath('.//div[contains(., "Altersverifikation")]'):
            if story:
                self.db['stories'].update_one({'_id': story['_id']}, {'$set': {'ageVerification': True}})
            else:
                self.db['stories'].update_one({'url': response.url}, {'$set': {'ageVerification': True}})
            return

        if response.css('div#content > div.pageviewframe').xpath('.//div[contains(., "Geschichte wurde gesperrt")]'):
            if story:
                self.db['stories'].update_one({'_id': story['_id']}, {'$set': {'isLocked': True}})
            else:
                self.db['stories'].update_one({'url': response.url}, {'$set': {'isLocked': True}})
            return

        if story and 'url' in story and story['url'] != response.url and len(story['url'].split('/')) > 5 and len(response.url.split('/')) > 5:
            if story:
                self.db['stories'].update_one({'_id': story['_id']}, {'$set': {'isRedirected': True, 'redirectedTo': response.url}})
            else:
                self.db['stories'].update_one({'url': story['url']}, {'$set': {'isRedirected': True, 'redirectedTo': response.url}})
            return

        # general data
        loader.add_value('source', 'FanFiktion')
        story_path = response.css('#ffcbox-story-topic-1 a::text').getall()
        if story_path:
            loader.add_value('genre', story_path[1])
            loader.add_value('fandom', story_path[2:-1])

        # left side data
        left = loader.nested_css('div.story-left')
        left_sel = response.css('div.story-left')
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
        if not user_url:
            user_url_sub = left_sel.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
            user_url = response.urljoin(user_url_sub)
        left.add_value('authorUrl', user_url)
        left.add_value('url', response.url)
        if len(response.url.split('/')) > 4:
            left.add_value('iid', response.url.split('/')[4])
        published_on = left_sel.xpath('.//span[contains(@title, "erstellt")]/../text()').getall()
        if published_on:
            left.add_value('publishedOn', get_date(''.join(published_on)))
        reviewed_on = left_sel.xpath('.//span[contains(@title, "aktualisiert")]/../text()').getall()
        if reviewed_on:
            left.add_value('reviewedOn', get_date(''.join(reviewed_on)))
        total_chapter_count = left_sel.xpath('.//span[contains(@title, "Kapitel")]/..').css('span.semibold::text').get()
        if total_chapter_count:
            left.add_value('totalChapterCount', total_chapter_count)
        if total_review_count:
            left.add_value('totalReviewCount', total_review_count)

        yield loader.load_item()

        if story:
            current_chapter_count = self.db['chapters'].count_documents({'storyId': story['_id']})
            if total_chapter_count and str_to_int(current_chapter_count) < str_to_int(total_chapter_count):
                yield from self.parse_chapter(response, response.url, story, total_chapter_count)

    def parse_chapter(self, response, story_url=None, story=None, chapter=None, total_chapter_count='0'):
        """Parses chapters and following."""

        if response.css('div#content > div.pageviewframe').xpath('.//div[contains(., "Meldung")]') or response.css('div#content > div.story > div.pageviewframe').xpath('.//div[contains(., "Altersverifikation")]'):
            self.db['chapters'].update_one({'url': response.url}, {'$set': {'ageVerification': True}})
            return
        if response.css('div#content > div.pageviewframe').xpath('.//div[contains(., "Geschichte wurde gesperrt")]'):
            self.logger.error('Chapter got locked from url %s', response.url)
            self.db['chapters'].update_one({'url': response.url}, {'$set': {'isLocked': True}})
            return

        right_sel = response.css('div.story-right')
        loader = ItemLoader(item=Chapter(), selector=right_sel)
        loader.add_value('storyUrl', story_url)
        loader.add_value('url', response.url)
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

        if chapter and 'url' in chapter and chapter['url'] != response.url:
            self.db.chapters.update_one({'url': chapter['url']}, {'$set': {'isRedirected': True, 'redirectedTo': response.url}})
        else:
            yield loader.load_item()

        # if not story:  # story is missing so far
        #     next_chapter = right_sel.xpath('.//a[contains(@title, "nächstes Kapitel")]/@href').get()
        #     if next_chapter:
        #         yield response.follow(next_chapter, callback=self.parse_chapter, cb_kwargs=dict(story_url=story_url, story=story, total_chapter_count=total_chapter_count))
        # else:  # chapters are missing
        #     for chapter_number in range(1, str_to_int(total_chapter_count)):
        #         chapter = self.db['chapters'].find_one({'storyId': ObjectId(story['_id']), 'number': chapter_number, 'isPreliminary': False})
        #         if not chapter:
        #             url_parts = response.url.split('/')
        #             url_parts[-2] = str(chapter_number)
        #             chapter_url = '/'.join(url_parts)
        #             yield Request(chapter_url, callback=self.parse_chapter, cb_kwargs=dict(story_url=story_url, story=story, total_chapter_count=total_chapter_count))

    def parse_user(self, response, user=None):
        """Parses user item."""

        loader = ItemLoader(item=User(), selector=response)

        # general data
        loader.add_value('source', 'FanFiktion')
        loader.add_css('username', 'div.userprofile-bio-table-outer h2')
        loader.add_value('url', response.url)

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
        # not working since box with content is loaded via javascript
        # story_related.add_value('favoredStories', response.urljoin(response.css('div#ffcbox-stories-layer-favstorynickdetails a.hint--large::attr(href)').getall()))
        # story_related.add_value('favoredAuthors', response.urljoin(response.css('div#ffcbox-stories-layer-favauthornickdetails a::attr(href)').getall()))

        yield loader.load_item()

    def parse_reviews(self, response, story_url):
        """Parses review items."""
        if response.status != 200:
            raise CloseSpider('Closing spider due to HTTP error')

        for review in response.css('div.review'):
            loader = ItemLoader(item=Review(), selector=review)
            loader.add_value('url', response.url)

            # left side data
            left = loader.nested_css('div.review-left')
            left_sel = review.css('div.review-left')
            user_url = left_sel.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
            if user_url:
                left.add_value('userUrl', response.urljoin(user_url))
                if self.db['users'].find_one({'url': response.urljoin(user_url), 'isPreliminary': False}) is None:
                    yield response.follow(user_url, callback=self.parse_user)

            reviewed_at = left_sel.xpath('.//div[contains(text(), "Uhr")]/text()').get()
            if reviewed_at:
                left.add_value('reviewedAt', get_datetime(reviewed_at))
            if left_sel.xpath('.//i[contains(text(), "Kapitel")]'):  # review for Chapter
                reviewable_type = 'Chapter'
                left.add_value('reviewableType', reviewable_type)
                reviewable_url = left_sel.xpath('.//a[starts-with(@href, "/s/")]/@href').get()
                if reviewable_url:
                    left.add_value('reviewableUrl', response.urljoin(reviewable_url))
            else:  # review for Story
                reviewable_type = 'Story'
                left.add_value('reviewableType', reviewable_type)
                reviewable_url = story_url
                left.add_value('reviewableUrl', response.urljoin(reviewable_url))

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
                    reply_loader.add_value('userUrl', response.urljoin(reply_user_url))
                reply_reviewed_at = reply.css('div.bold.padded-vertical *::text').getall()[-1]
                if reply_reviewed_at:
                    reply_loader.add_value('reviewedAt', get_datetime(reply_reviewed_at))
                reply_loader.add_css('content', 'span.usercontent')
                if reviewable_type:
                    reply_loader.add_value('reviewableType', reviewable_type)
                    reply_loader.add_value('parentReviewableType', reviewable_type)
                if reviewable_url:
                    reply_loader.add_value('reviewableUrl', response.urljoin(reviewable_url))
                    reply_loader.add_value('parentReviewableUrl', response.urljoin(reviewable_url))
                if user_url:
                    reply_loader.add_value('parentUserUrl', response.urljoin(user_url))
                if reviewed_at:
                    reply_loader.add_value('parentReviewedAt', get_datetime(reviewed_at))
                yield reply_loader.load_item()

            yield loader.load_item()

        next_reviews = response.css('link[rel="next"]::attr(href)').get()
        if next_reviews:
            yield response.follow(next_reviews, callback=self.parse_reviews, cb_kwargs=dict(story_url=story_url))
