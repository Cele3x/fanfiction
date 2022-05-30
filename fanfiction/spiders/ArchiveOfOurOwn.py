import sys

from scrapy.exceptions import CloseSpider
from typing import Union

from fanfiction.settings import MONGO_URI, MONGO_DB
from pymongo import MongoClient
from bson.objectid import ObjectId
from abc import ABC
from fanfiction.utilities import get_datetime, get_date, str_to_int
from scrapy.http import Request
from scrapy import signals
from pydispatch import dispatcher
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from w3lib.html import replace_tags, replace_escape_chars
from fanfiction.items import Story, Chapter, User, Review
from urllib.parse import urlencode
from datetime import datetime
from dateutil.relativedelta import relativedelta


def find_story_status(text: str, reviewed_on: datetime) -> Union[str, None]:
    """Find story status inside HTML snippet.

    :param text: unformatted status text; e.g. "11/18"
    :param reviewed_on: last story update
    :return: story status
    """
    text_split = [x.strip() for x in text.split('/')]
    if len(text_split) != 2:
        return None
    p1 = str_to_int(text_split[0])
    p2 = sys.maxsize if text_split[1] in ['?', ''] else str_to_int(text_split[1])
    if type(p1) == int and type(p2) == int:
        if p1 == p2:
            return 'done'
        elif p1 < p2:
            year_delta = relativedelta(reviewed_on, datetime.now()).years
            if year_delta > 3:
                return 'cancelled'
            elif year_delta > 0:
                return 'paused'
            else:
                return 'work in progress'
        else:
            return None


class ArchiveOfOurOwnSpider(CrawlSpider, ABC):
    name = 'ArchiveOfOurOwn'
    download_delay = 1
    allowed_domains = ['archiveofourown.org']

    custom_settings = {
        # 'JOBDIR': 'crawls/FanFiction-Books',
    }

    start_urls = ['https://archiveofourown.org/media/Books%20*a*%20Literature/fandoms']
    start_urls_genre = 'Books & Literature'

    rules = (
        Rule(LinkExtractor(allow=r'\/tags\/Harry%20Potter', restrict_css='ol.fandom.index'), process_links='add_language_filter', process_request='adjust_request', callback='parse_fandom', follow=False),
    )

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.adult_cookie = {'name': 'view_adult', 'value': 'true', 'domain': 'archiveofourown.org', 'path': '/'}
        # SCRAPY SHELL:
        # from scrapy import Request
        # fetch(Request('https://archiveofourown.org/works/35789398?view_full_work=true&show_comments=true', cookies=[{'name': 'view_adult', 'value': 'true', 'domain': 'archiveofourown.org', 'path': '/'}]))

    def spider_closed(self, spider):
        self.client.close()

    def add_language_filter(self, links):
        params = {
            'work_search[language_id]': 'de'
        }
        for link in links:
            link.url = "%s?%s" % (link.url, urlencode(params))
        return links

    def adjust_request(self, request, _referer):
        request.cookies.update(self.adult_cookie)
        return request

    def parse_fandom(self, response):
        """Processes fandom by evaluating their type and passing it to the appropriate parser."""

        if response.status != 200:
            raise CloseSpider('Closing spider due to HTTP error')

        for item in response.css('li.work.group'):
            user_url_pseuds = response.urljoin(item.xpath('.//a[starts-with(@href, "/users/")]/@href').get())
            user_url = user_url_pseuds.rsplit('/', 2)[0]
            user_url_profile = "%s/%s" % (user_url, 'profile')
            story_url = response.urljoin(item.xpath('.//a[starts-with(@href, "/works/")]/@href').get())
            story_url_full_with_comments = "%s?%s" % (story_url, urlencode({'view_full_work': 'true', 'show_comments': 'true'}))
            if self.db['users'].find_one({'url': user_url, 'isPreliminary': False}) is None:
                yield Request(user_url_profile, callback=self.parse_user, cb_kwargs=dict(user_url=user_url))
            if self.db['stories'].find_one({'url': story_url, 'isPreliminary': False}) is None:
                yield Request(story_url_full_with_comments, cookies=[{'name': 'view_adult', 'value': 'true', 'domain': 'archiveofourown.org', 'path': '/'}], callback=self.parse_story, cb_kwargs=dict(user_url=user_url, story_url=story_url))

    def parse_user(self, response, user_url):
        """Parses user item."""
        loader = ItemLoader(item=User(), selector=response)

        loader.add_value('source', 'ArchiveOfOurOwn')
        loader.add_css('username', 'div.userprofile-bio-table-outer h2')
        loader.add_value('url', user_url)
        loader.add_css('bio', 'div.bio.module blockquote.userstuff')

        user_profile = loader.nested_css('div.user.home.profile')
        user_profile_sel = response.css('div.user.home.profile')
        joined_on = user_profile_sel.xpath('.//dt[contains(text(), "I joined on:")]/following-sibling::dd[1]/text()').get()
        user_profile.add_value('joinedOn', get_date(joined_on))
        user_profile.add_xpath('country', './/dt[contains(text(), "I live in:")]/following-sibling::dd[1]/text()')
        user_profile.add_css('username', 'div.primary.header.module h2.heading')

        # print(loader.load_item())
        # yield loader.load_item()

    def parse_story(self, response, user_url, story_url):
        """Parses story item."""
        loader = ItemLoader(item=Story(), selector=response)

        loader.add_value('source', 'ArchiveOfOurOwn')
        loader.add_value('url', story_url)
        loader.add_value('authorUrl', user_url)
        loader.add_value('genre', self.start_urls_genre)

        story_meta = loader.nested_css('dl.work.meta.group')
        story_meta_sel = response.css('dl.work.meta.group')
        story_meta.add_css('ratings', 'dd.rating.tags a.tag')
        story_meta.add_css('tags', 'dd.warning.tags a.tag')
        story_meta.add_css('pairings', 'dd.category.tags a.tag')
        story_meta.add_css('fandoms', 'dd.fandom.tags a.tag')
        story_meta.add_css('characters', 'dd.character.tags a.tag')
        story_meta.add_css('tags', 'dd.freeform.tags a.tag')  # TODO: necessary?
        published_on = story_meta_sel.xpath('.//dt[contains(text(), "Published:")]/following-sibling::dd[1]/text()').get()
        if published_on:
            story_meta.add_value('publishedOn', get_date(published_on))
        updated_on = story_meta_sel.xpath('.//dt[contains(text(), "Updated:")]/following-sibling::dd[1]/text()').get()
        if updated_on:
            story_meta.add_value('reviewedOn', get_date(updated_on))
        completed_on = story_meta_sel.xpath('.//dt[contains(text(), "Completed:")]/following-sibling::dd[1]/text()').get()
        if completed_on:
            story_meta.add_value('reviewedOn', get_date(completed_on))
        chapter_status = story_meta_sel.xpath('.//dt[contains(text(), "Chapters:")]/following-sibling::dd[1]/text()').get()
        if chapter_status:
            if updated_on:
                status = find_story_status(chapter_status, get_date(updated_on))
            elif completed_on:
                status = 'done'
            else:
                status = find_story_status(chapter_status, datetime.now())
            story_meta.add_value('status', status)

        story_preface = loader.nested_css('div#workskin div.preface.group')
        story_preface.add_css('title', 'h2.title.heading')
        story_preface.add_css('summary', 'div.summary.module blockquote.userstuff')

        # print(loader.load_item())
        # yield loader.load_item()
        # yield from self.parse_chapter(response, story_url)
        self.parse_chapter(response, story_url)

    def parse_chapter(self, response, story_url, story=None):
        """Parses chapters and following."""

        chapters = response.css('div#chapters > div.chapter')
        if not chapters:
            chapter = response.css('div#chapters')
            loader = ItemLoader(item=Chapter(), selector=chapter)
            loader.add_value('number', 1)
            loader.add_value('url', response.url)
            loader.add_css('content', 'div.userstuff p')
            print(loader.load_item())
        else:
            for chapter in chapters:
                loader = ItemLoader(item=Chapter(), selector=chapter)
                chapter_id = chapter.xpath('@id').get()
                chapter_number = chapter_id.split('-')[-1]
                loader.add_value('number', chapter_number)
                title = chapter.css('h3.title ::text').getall()[-1].split(':', 1)[-1]
                loader.add_value('title', title)
                chapter_url = chapter.css('h3.title a::attr(href)').get()
                loader.add_value('url', chapter_url)
                loader.add_css('content', 'div.userstuff p')
                print(loader.load_item())

    def parse_reviews(self, response, chapter_url, chapter=None):
        """Parses reviews."""

        loader = ItemLoader(item=Review(), selector=response)

