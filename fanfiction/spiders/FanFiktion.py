from abc import ABC
from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.loader import ItemLoader
from fanfiction.items import Story, User


class FanfiktionSpider(CrawlSpider, ABC):
    name = 'FanFiktion'
    # download_delay = 1
    allowed_domains = ['fanfiktion.de']
    # start_urls = ['https://www.fanfiktion.de/Fanfiction/c/100000000']
    start_urls = ['https://www.fanfiktion.de/Tabletop-Rollenspiele/c/108000000']

    rules = (
        # Rule(LinkExtractor(allow=r'/Anime-Manga/'), callback='parse_item', follow=False),
        # Rule(LinkExtractor(allow=r'\/c\/', restrict_css='div.storylist div.grid-rowcount3'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'\/c\/', restrict_css='div.storylist'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'^\/u\/', restrict_css='div.storylist'), callback='parse_user', follow=True),
        # Rule(LinkExtractor(allow=r'^\/s\/', restrict_css='div.storylist'), callback='parse_story', follow=True),
    )

    def parse_item(self, response):
        # category_list = response.css('span.topic-title-big a::text').getall()
        # print(category_list)
        for item in response.css('div.storylist-item'):
            story_url = 'https://www.fanfiktion.de' + item.css('div.huge-font a::attr(href)').get()
            user_url = 'https://www.fanfiktion.de' + item.css('div.padded-small-vertical a::attr(href)').get()
            yield Request(user_url, callback=self.parse_user)
            yield Request(story_url, callback=self.parse_story)

    def parse_story(self, response):
        loader = ItemLoader(item=Story(), selector=response)
        left = loader.nested_css('div.story-left')
        left.add_css('title', 'div.huge-font a')
        left.add_value('url', response.url)
        loader.add_value('createdAt', datetime.utcnow())
        loader.add_value('updatedAt', datetime.utcnow())
        yield loader.load_item()

    def parse_user(self, response):
        loader = ItemLoader(item=User(), selector=response)
        loader.add_css('name', 'div.userprofile-bio-table-outer h2')
        loader.add_value('url', response.url)
        loader.add_value('createdAt', datetime.utcnow())
        loader.add_value('updatedAt', datetime.utcnow())
        yield loader.load_item()
