from abc import ABC
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime
from ..items import Story, User


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
    )

    def parse_item(self, response):
        # self.logger.info('Got successful response from {}'.format(response.url))
        category_list = response.css('span.topic-title-big a::text').getall()
        for item in response.css('div.storylist-item'):
            story = Story({
                'title': item.css('div.storylist-leftcol div.huge-font a::text').get(),
                'url': item.css('div.storylist-leftcol div.huge-font a::attr(href)').get(),
                'categoryList': category_list,
                'updatedAt': datetime.datetime.utcnow(),
                'createdAt': datetime.datetime.utcnow(),
                # 'author': User({'name': 'Test'})
            })
            yield story
