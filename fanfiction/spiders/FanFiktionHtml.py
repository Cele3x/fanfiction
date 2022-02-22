import csv
import tarfile
import os
import os.path
from abc import ABC
from datetime import datetime
from scrapy import signals
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

    def __init__(self, *a, **kw):
        super(FanfiktionHtmlSpider, self).__init__(*a, **kw)
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
        state_attrs = ['done_story_urls', 'done_user_urls', 'done_reviews_urls', 'open_story_urls', 'open_user_urls', 'open_reviews_urls', 'failed_story_urls', 'failed_user_urls', 'failed_reviews_urls']
        for state_attr in state_attrs:
            self.state[state_attr] = getattr(self.state, state_attr, set())

        self.read_urls_into_state()
        self.print_stats()

    def handle_spider_idle(self, spider):
        spider.logger.info('Spider idle: %s', spider.name)

        # process open urls
        while self.state.get('open_story_urls', set()):
            url = self.state.get('open_story_urls').pop()
            spider.logger.info('Crawling story: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_story), spider)
        while self.state.get('open_user_urls', set()):
            url = self.state.get('open_user_urls').pop()
            spider.logger.info('Crawling user: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_user), spider)
        while self.state.get('open_reviews_urls', set()):
            url = self.state.get('open_reviews_urls').pop()
            spider.logger.info('Crawling reviews: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_reviews), spider)

        # process failed urls
        while self.state.get('failed_story_urls', set()):
            url = self.state.get('failed_story_urls').pop()
            spider.logger.info('Crawling story: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_story), spider)
        while self.state.get('failed_user_urls', set()):
            url = self.state.get('failed_user_urls').pop()
            spider.logger.info('Crawling user: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_user), spider)
        while self.state.get('failed_reviews_urls', set()):
            url = self.state.get('failed_reviews_urls').pop()
            spider.logger.info('Crawling reviews: %s', url)
            self.crawler.engine.crawl(Request(url, callback=self.save_reviews), spider)

    def handle_spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)

        # set stats
        state_attrs = ['open_story_urls', 'open_user_urls', 'open_reviews_urls', 'failed_story_urls', 'failed_user_urls', 'failed_reviews_urls']
        for state_attr in state_attrs:
            self.crawler.stats.set_value(state_attr, len(self.state.get(state_attr, set())))
        self.crawler.stats.set_value('crawled_stories', self.state.get('story_items'), 0)
        self.crawler.stats.set_value('crawled_users', self.state.get('user_items'), 0)
        self.crawler.stats.set_value('crawled_reviews', self.state.get('reviews_items'), 0)

        # # archive files
        # archive_files('pages/stories/')
        # archive_files('pages/users/')
        # archive_files('pages/reviews/')

    def read_urls_into_state(self):
        self.logger.info('Reading done story urls from CSV file into state...')
        with open('pages/stories.csv') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                self.state['done_story_urls'].add(row[1])
        self.logger.info('Done')
        self.logger.info('Reading done user urls from CSV file into state...')
        with open('pages/users.csv') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                self.state['done_user_urls'].add(row[1])
        self.logger.info('Done')
        self.logger.info('Reading done reviews urls from CSV file into state...')
        with open('pages/reviews.csv') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                self.state['done_reviews_urls'].add(row[1])
        self.logger.info('Done')

    def print_stats(self):
        self.logger.info('Stories: %d [Done: %d, Open: %d]', self.state.get('story_items', 0), len(self.state.get('done_story_urls', set())), len(self.state.get('open_story_urls', set())))
        self.logger.info('Users: %d [Done: %d, Open: %d]', self.state.get('user_items', 0), len(self.state.get('done_user_urls', set())), len(self.state.get('open_user_urls', set())))
        self.logger.info('Reviews: %d [Done: %d, Open: %d]', self.state.get('reviews_items', 0), len(self.state.get('done_reviews_urls', set())), len(self.state.get('open_reviews_urls', set())))

    def parse_storylist(self, response):
        for item in response.css('div.storylist-item'):
            user_url = item.xpath('.//a[starts-with(@href, "/u/")]/@href').get()
            story_url = item.xpath('.//a[starts-with(@href, "/s/")]/@href').get()
            reviews_url = item.xpath('.//a[starts-with(@href, "/r/s/")]/@href').get()

            if story_url and response.urljoin(story_url) not in self.state['done_story_urls']:
                self.state['open_story_urls'].add(response.urljoin(story_url))
                yield response.follow(response.urljoin(story_url), callback=self.save_story)
            if user_url and response.urljoin(user_url) not in self.state['done_user_urls']:
                self.state['open_user_urls'].add(response.urljoin(user_url))
                yield response.follow(response.urljoin(user_url), callback=self.save_user)
            if reviews_url and response.urljoin(reviews_url) not in self.state['done_reviews_urls']:
                self.state['open_reviews_urls'].add(response.urljoin(reviews_url))
                yield response.follow(response.urljoin(reviews_url), callback=self.save_reviews)

    def save_story(self, response: any):
        # check for failed request
        if response.status == 403 or response.status == 404:
            self.crawler.stats.inc_value('failed_url_count')
            self.state['failed_story_urls'].add(response.url)
            return

        # get last part of path while omitting preceeding 'https://www.fanfiktion.de/s/'
        parts = response.url.split('/')
        uid = parts[4]
        chapter = parts[5]
        title = parts[6]
        filename = '%s_%s_%s.html' % (uid, chapter, title)

        # save url data into csv file
        with open('pages/stories.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([filename, response.url, uid, title, chapter])

        # save html file
        with open('pages/stories/' + filename, 'wb') as f:
            f.write(response.body)

        # increment item count and archive if due
        self.state['story_items'] = self.state.get('story_items', 0) + 1
        self.state['item_count'] = self.state.get('item_count', 0) + 1
        if self.state['story_items'] % 1000 == 0:  # every 1000 items
            archive_files('pages/stories/')

        # remove story url from open urls
        self.state['open_story_urls'].discard(response.url)

        # check for next chapter and follow
        next_chapter = response.css('div.story-right').xpath('.//a[contains(@title, "nächstes Kapitel")]/@href').get()
        if next_chapter and response.urljoin(next_chapter) not in self.state['done_story_urls']:
            self.state['open_story_urls'].add(response.urljoin(next_chapter))
            yield response.follow(next_chapter, callback=self.save_story)

    def save_user(self, response: any):
        # check for failed requests
        if response.status == 403 or response.status == 404:
            self.crawler.stats.inc_value('failed_url_count')
            self.state['failed_user_urls'].add(response.url)
            return

        # get last part of path while omitting preceeding 'https://www.fanfiktion.de/u/'
        parts = response.url.split('/')
        uid = parts[4]
        filename = '%s.html' % uid

        # save url data into csv file
        with open('pages/users.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([filename, response.url, uid])

        # save html file
        with open('pages/users/' + filename, 'wb') as f:
            f.write(response.body)

        # increment item count and archive if due
        self.state['user_items'] = self.state.get('user_items', 0) + 1
        self.state['item_count'] = self.state.get('item_count', 0) + 1
        if self.state['user_items'] % 1000 == 0:  # every 1000 items
            archive_files('pages/users/')

        # remove user url from open urls
        self.state['open_user_urls'].discard(response.url)

    def save_reviews(self, response: any):
        # check for failed requests
        if response.status == 403 or response.status == 404:
            self.crawler.stats.inc_value('failed_url_count')
            self.state['failed_reviews_urls'].add(response.url)
            return

        # get last part of path while omitting preceeding 'https://www.fanfiktion.de/r/s/'
        parts = response.url.split('/')
        uid = parts[5]
        sorted_by = parts[6]
        chapter = parts[7]
        page = parts[8]
        filename = '%s_%s_%s_%s.html' % (uid, sorted_by, chapter, page)

        # save url data into csv file
        with open('pages/reviews.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([filename, response.url, uid, page])

        # save html file
        with open('pages/reviews/' + filename, 'wb') as f:
            f.write(response.body)

        # increment item count and archive if due
        self.state['reviews_items'] = self.state.get('reviews_items', 0) + 1
        self.state['item_count'] = self.state.get('item_count', 0) + 1
        if self.state['reviews_items'] % 1000 == 0:  # every 1000 items
            archive_files('pages/reviews/')

        # remove reviews url from open urls
        self.state['open_reviews_urls'].discard(response.url)

        # check for next reviews and follow
        next_reviews = response.css('link[rel="next"]::attr(href)').get()
        if next_reviews and response.urljoin(next_reviews) not in self.state['done_reviews_urls']:
            self.state['open_reviews_urls'].add(response.urljoin(next_reviews))
            yield response.follow(next_reviews, callback=self.save_reviews)
