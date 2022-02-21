import csv
import tarfile
import os
import os.path
from abc import ABC
from datetime import datetime
from time import sleep

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


def archive_files(filepath: str, min_size: int = 1, with_csv: bool = False) -> None:
    try:
        filelist = [os.path.join(filepath, file) for file in os.listdir(filepath) if file.endswith('.html') or (with_csv and file.endswith('.csv'))]
        if len(filelist) > min_size:
            archive_name = filepath + datetime.now().strftime("%Y%m%d%H%M%S%f") + '_archive.tar.gz'
            with tarfile.open(archive_name, "w:gz") as tar:
                for file in filelist:
                    tar.add(file, arcname=file.split('/')[-1])  # add to archive
                    os.remove(file)  # delete file
            print('Archive: ', archive_name)
    except FileNotFoundError:
        print('Archive could not be created because path was not found: ', filepath)


class FanfiktionHtmlSpider(CrawlSpider, ABC):
    name = 'FanFiktionHtml'
    download_delay = 1
    allowed_domains = ['fanfiktion.de']

    custom_settings = {
        'JOBDIR': 'crawls/Buecher-Html',
    }

    start_urls = ['https://www.fanfiktion.de/Buecher/c/103000000']

    rules = (
        Rule(LinkExtractor(allow=r'\/c\/', restrict_css='div.storylist'), callback='parse_storylist', follow=True),
    )

    story = {
        'type': 'story',
        'csv_filepath': 'pages/stories/story_urls.csv',
        'html_path': 'pages/stories/',
        'url_parts': 4,
        'state_count_name': 'story_items'
    }
    user = {
        'type': 'user',
        'csv_filepath': 'pages/users/user_urls.csv',
        'html_path': 'pages/users/',
        'url_parts': 4,
        'state_count_name': 'user_items'
    }
    reviews = {
        'type': 'reviews',
        'csv_filepath': 'pages/reviews/reviews_urls.csv',
        'html_path': 'pages/reviews/',
        'url_parts': 5,
        'state_count_name': 'reviews_items'
    }

    def __init__(self, *a, **kw):
        super().__init__(a, kw)
        self.state = getattr(self, 'state', {})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FanfiktionHtmlSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.handle_spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.handle_spider_idle, signals.spider_idle)
        crawler.signals.connect(spider.handle_spider_closed, signals.spider_closed)
        return spider

    def handle_spider_opened(self, spider):
        spider.logger.info('Spider opened: %s', spider.name)

        # get or initialize state attributes
        state_attrs = ['open_story_urls', 'open_user_urls', 'open_reviews_urls', 'failed_story_urls', 'failed_user_urls', 'failed_reviews_urls']
        for state_attr in state_attrs:
            self.state[state_attr] = getattr(self.state, state_attr, set())

        self.print_stats()

    def handle_spider_idle(self, spider):
        spider.logger.info('Spider idle: %s', spider.name)

        while self.state.get('open_story_urls', set()):
            url = self.state.get('open_story_urls').pop()
            print('Crawling story: ', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_item, cb_kwargs=dict(item=self.story)), spider)
        while self.state.get('open_user_urls', set()):
            url = self.state.get('open_user_urls').pop()
            print('Crawling user: ', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_item, cb_kwargs=dict(item=self.user)), spider)
        while self.state.get('open_reviews_urls', set()):
            url = self.state.get('open_reviews_urls').pop()
            print('Crawling reviews: ', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_item, cb_kwargs=dict(item=self.reviews)), spider)

        if self.state.get('open_story_urls') or self.state.get('open_user_urls') or self.state.get('open_reviews_urls'):
            sleep(10)
            raise DontCloseSpider

    def handle_spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)

        # set stats
        self.crawler.stats.set_value('failed_user_urls', len(self.state.get('failed_user_urls', set())))
        self.crawler.stats.set_value('failed_story_urls', len(self.state.get('failed_story_urls', set())))
        self.crawler.stats.set_value('failed_reviews_urls', len(self.state.get('failed_reviews_urls', set())))
        self.crawler.stats.set_value('crawled_users', self.state.get('user_items'), 0)
        self.crawler.stats.set_value('crawled_stories', self.state.get('story_items'), 0)
        self.crawler.stats.set_value('crawled_reviews', self.state.get('reviews_items'), 0)
        self.crawler.stats.set_value('open_user_urls', len(self.state.get('open_user_urls', set())))
        self.crawler.stats.set_value('open_story_urls', len(self.state.get('open_story_urls', set())))
        self.crawler.stats.set_value('open_reviews_urls', len(self.state.get('open_reviews_urls', set())))

        # archive files
        # archive_files(self.story['html_path'], with_csv=True)
        # archive_files(self.user['html_path'], with_csv=True)
        # archive_files(self.reviews['html_path'], with_csv=True)

    def print_stats(self):
        self.logger.info('Stories: %d [%d]', self.state.get('story_items', 0), len(self.state.get('open_story_urls', set())))
        self.logger.info('Users: %d [%d]', self.state.get('user_items', 0), len(self.state.get('open_user_urls', set())))
        self.logger.info('Reviews: %d [%d]', self.state.get('reviews_items', 0), len(self.state.get('open_reviews_urls', set())))

    def parse_storylist(self, response):
        for item in response.css('div.storylist-item'):
            user_url = item.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
            story_url = item.xpath('.//a[starts-with(@href, "/s/")]/@href').get()
            reviews_url = item.xpath('.//a[starts-with(@href, "/r/s/")]/@href').get()

            if story_url:
                self.state['open_story_urls'].add(response.urljoin(story_url))
                yield response.follow(response.urljoin(story_url), callback=self.save_item, cb_kwargs=dict(item=self.story))
            if user_url:
                self.state['open_user_urls'].add(response.urljoin(user_url))
                yield response.follow(response.urljoin(user_url), callback=self.save_item, cb_kwargs=dict(item=self.user))
            if reviews_url:
                self.state['open_reviews_urls'].add(response.urljoin(reviews_url))
                yield response.follow(response.urljoin(reviews_url), callback=self.save_item, cb_kwargs=dict(item=self.reviews))

    def save_item(self, response: any, item: dict):
        filename = '_'.join(response.url.split("/")[item['url_parts']:]) + '.html'
        with open(item['csv_filepath'], 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            if response.status == 403 or response.status == 404:
                self.crawler.stats.inc_value('failed_url_count')
                if item['type'] == 'story':
                    self.state['failed_story_urls'].add(response.url)
                elif item['type'] == 'user':
                    self.state['failed_user_urls'].add(response.url)
                elif item['type'] == 'reviews':
                    self.state['failed_reviews_urls'].add(response.url)
                writer.writerow(['FAILED', filename, response.url])
                return
            else:
                writer.writerow([filename, response.url])
        with open(item['html_path'] + filename, 'wb') as f:
            f.write(response.body)

        self.state[item['state_count_name']] = self.state.get(item['state_count_name'], 0) + 1
        self.state['item_count'] = self.state.get('item_count', 0) + 1
        if self.state['item_count'] % 100 == 0:  # every 100 items
            self.print_stats()
        if self.state['item_count'] % 100 == 0:  # every 1000 items
            archive_files(item['html_path'])

        if item['type'] == 'story':
            self.state['open_story_urls'].discard(response.url)
            next_chapter = response.css('div.story-right').xpath('.//a[contains(@title, "nächstes Kapitel")]/@href').get()
            if next_chapter:
                self.state['open_story_urls'].add(response.urljoin(next_chapter))
                yield response.follow(next_chapter, callback=self.save_item, cb_kwargs=dict(item=item))
        elif item['type'] == 'user':
            self.state['open_user_urls'].discard(response.url)
        elif item['type'] == 'reviews':
            self.state['open_reviews_urls'].discard(response.url)
            next_reviews = response.css('link[rel="next"]::attr(href)').get()
            if next_reviews:
                self.state['open_reviews_urls'].add(response.urljoin(next_reviews))
                yield response.follow(next_reviews, callback=self.save_item, cb_kwargs=dict(item=item))
