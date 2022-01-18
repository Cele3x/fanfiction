import re
from abc import ABC

from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from w3lib.html import replace_tags, replace_escape_chars

from fanfiction.items import Story, Chapter, User


def find_story_definitions(text: str) -> list:
    """Find story definitions inside HTML snippet.

    :param text: str
        with HTML elements containing tags and excape chars
    :return: list
        with elements split by ' / ' character
    """
    text = replace_escape_chars(text)
    text = replace_tags(text, ' / ')
    return list(filter(None, [x.strip() for x in text.split(' / ')]))


class FanfiktionSpider(CrawlSpider, ABC):
    name = 'FanFiktion'
    download_delay = 1
    allowed_domains = ['fanfiktion.de']
    # start_urls = ['https://www.fanfiktion.de/Fanfiction/c/100000000']
    start_urls = ['https://www.fanfiktion.de/Tabletop-Rollenspiele/c/108000000']

    rules = (
        # Rule(LinkExtractor(allow=r'\/c\/', restrict_css='div.storylist div.grid-rowcount3'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'\/c\/', restrict_css='div.storylist'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """Processes item by evaluating their type and passing it to the appropriate parser."""
        for item in response.css('div.storylist-item'):
            user_url = response.urljoin(item.css('div.padded-small-vertical a::attr(href)').get())
            story_url = response.urljoin(item.css('div.huge-font a::attr(href)').get())
            chapter_url = response.urljoin(item.css('div.huge-font a::attr(href)').get())
            yield Request(user_url, callback=self.parse_user)
            yield Request(story_url, callback=self.parse_story)
            # yield Request(chapter_url, callback=self.parse_chapter)
            # for chapter in response.css('#kA option'):
            #     onchange = chapter.xpath("//../select[@id = 'kA']//@onchange").get()
            #     href_parts = re.findall(r'\'(.*?)\'', onchange)
            #     chapter_url = response.urljoin(href_parts[0] + chapter.css('::attr(value)').get() + href_parts[1])
            #     yield Request(chapter_url, callback=self.parse_chapter)

    def parse_story(self, response):
        """Parses story item."""
        loader = ItemLoader(item=Story(), selector=response)

        # general data
        loader.add_value('source', 'FanFiktion')
        story_path = response.css('#ffcbox-story-topic-1 a').getall()
        if story_path:
            loader.add_value('genre', story_path[1])
            loader.add_value('fandom', story_path[2])

        # left side data
        left = loader.nested_css('div.story-left')
        left.add_css('title', 'h4.huge-font')
        summary_text = response.css('div#story-summary-inline *::text').get()
        if summary_text:
            if summary_text == '(Der Autor hat keine Kurzbeschreibung zu dieser Geschichte verfasst.)':
                summary_text = None
            left.add_value('summary', summary_text)
        story_definitions_block = response.css('div.small-font.center.block')
        if story_definitions_block:
            definitions = find_story_definitions(story_definitions_block.get())
            left.add_value('category', definitions[0])
            left.add_value('topics', definitions[1])
            left.add_value('rating', definitions[2])
            left.add_value('pairing', definitions[3])
        if response.xpath('//span[contains(@title, "Fertiggestellt")]'):
            left.add_value('status', 'done')
        elif response.xpath('//span[contains(@title, "in Arbeit")]'):
            left.add_value('status', 'work in progress')
        elif response.xpath('//span[contains(@title, "Pausiert")]'):
            left.add_value('status', 'paused')
        elif response.xpath('//span[contains(@title, "Abgebrochen")]'):
            left.add_value('status', 'cancelled')
        left.add_xpath('likes', '//span[contains(@title, "Empfehlungen")]/../text()')
        left.add_css('characters', 'span.badge-character')
        left.add_value('authorUrl', response.urljoin(response.css('div.center.small-font a::attr(href)').get()))
        left.add_value('url', response.url)
        left.add_xpath('storyCreatedAt', '//span[contains(@title, "erstellt")]/../text()')
        left.add_xpath('storyUpdatedAt', '//span[contains(@title, "aktualisiert")]/../text()')

        # first chapter has to be scraped here because scrapy will detect that the page had already been scraped and omit it
        chapter_loader = ItemLoader(item=Chapter(), selector=response.css('div.story-right'))
        chapter_loader.add_value('storyUrl', response.url)
        chapter_loader.add_css('content', 'div#storytext')
        chapter_number = response.xpath('//select[@id="kA"]/option[contains(@selected, "selected")]/@value').get()
        if chapter_number:
            chapter_loader.add_value('number', chapter_number)
        chapter_title = response.xpath('//select[@id="kA"]/option[contains(@selected, "selected")]/text()').get()
        if chapter_title:
            chapter_title = re.sub(r'^\d+\.\s?', '', chapter_title)
            chapter_loader.add_value('title', chapter_title)

        yield loader.load_item()
        yield chapter_loader.load_item()

        next_chapter = response.xpath('//a[contains(@title, "nächstes Kapitel")]/@href').get()
        if next_chapter is not None:
            print('CHAPTER 2')
            yield response.follow(next_chapter, callback=self.parse_chapter)

    def parse_chapter(self, response):
        """Parses chapter 2 and following."""
        loader = ItemLoader(item=Chapter(), selector=response)
        loader.add_value('storyUrl', response.url)
        loader.add_css('content', 'div#storytext')
        chapter_number = response.xpath('//select[@id="kA"]/option[contains(@selected, "selected")]/@value').get()
        if chapter_number:
            loader.add_value('number', chapter_number)
        chapter_title = response.xpath('//select[@id="kA"]/option[contains(@selected, "selected")]/text()').get()
        if chapter_title:
            chapter_title = re.sub(r'^\d+\.\s?', '', chapter_title)
            loader.add_value('title', chapter_title)
        yield loader.load_item()

        next_chapter = response.xpath('//a[contains(@title, "nächstes Kapitel")]/@href').get()
        if next_chapter is not None:
            print('CHAPTER 3 OR FOLLOWING')
            yield response.follow(next_chapter, callback=self.parse_chapter)

    def parse_user(self, response):
        """Parses user item."""
        loader = ItemLoader(item=User(), selector=response)
        loader.add_css('name', 'div.userprofile-bio-table-outer h2')
        loader.add_value('url', response.url)
        yield loader.load_item()
