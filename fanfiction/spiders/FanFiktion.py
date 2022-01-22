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
    download_delay = 2
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
            yield Request(user_url, callback=self.parse_user)
            yield Request(story_url, callback=self.parse_story)

    def parse_story(self, response):
        """Parses story item."""
        loader = ItemLoader(item=Story(), selector=response)

        # general data
        loader.add_value('source', 'FanFiktion')
        story_path = response.css('#ffcbox-story-topic-1 a').getall()
        if story_path:
            loader.add_value('genre', story_path[1])
            loader.add_value('fandoms', story_path[2])

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
        left.add_xpath('publishedOn', '//span[contains(@title, "erstellt")]/../text()')
        left.add_xpath('reviewedOn', '//span[contains(@title, "aktualisiert")]/../text()')

        yield loader.load_item()
        yield from self.parse_chapter(response)

    def parse_chapter(self, response):
        """Parses chapters and following."""
        loader = ItemLoader(item=Chapter(), selector=response)
        loader.add_value('storyUrl', response.url)
        loader.add_css('content', 'div#storytext')
        loader.add_xpath('publishedOn', '//span[contains(@title, "Kapitel erstellt am")]/../text()')
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
            yield response.follow(next_chapter, callback=self.parse_chapter)

    def parse_user(self, response):
        """Parses user item."""
        loader = ItemLoader(item=User(), selector=response)
        loader.add_css('username', 'div.userprofile-bio-table-outer h2')
        loader.add_value('url', response.url)

        bio_table = loader.nested_css('div.userprofile-bio-table')
        bio_table.add_xpath('firstName', '//div[contains(text(), "Vorname")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('lastName', '//div[contains(text(), "Nachname")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('locatedAt', '//div[contains(text(), "Wohnort")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        bio_table.add_xpath('country', '//div[contains(text(), "Land")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')
        gender = response.css('div.userprofile-bio-table').xpath('//div[contains(text(), "Geschlecht")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()').get()
        if gender == 'männlich':
            bio_table.add_value('gender', 'male')
        elif gender == 'weiblich':
            bio_table.add_value('gender', 'female')
        elif gender == 'divers':
            bio_table.add_value('gender', 'other')
        bio_table.add_xpath('age', '//div[contains(text(), "Alter")]/../descendant-or-self::*/div[count(preceding-sibling::*) >= 1]/text()')

        story_related = loader.nested_css('div#ffcbox-stories')
        if response.css('div#ffcbox-stories-layer-aboutme div.status-message').xpath('//div[contains(text(), "Dieser Benutzer hat keine Informationen über sich veröffentlicht.")]'):
            story_related.add_value('bio', None)
        else:
            story_related.add_css('bio', 'div#ffcbox-stories-layer-aboutme')
        # not working since box with content is loaded via javascript
        # story_related.add_value('favoredStories', response.urljoin(response.css('div#ffcbox-stories-layer-favstorynickdetails a.hint--large::attr(href)').getall()))
        # story_related.add_value('favoredAuthors', response.urljoin(response.css('div#ffcbox-stories-layer-favauthornickdetails a::attr(href)').getall()))

        yield loader.load_item()
