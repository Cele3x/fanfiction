# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags, replace_tags, replace_escape_chars, replace_entities


def replace_tags_with_commas(value: str) -> str:
    """Replaces HTML tags with commas.

    :param value: str
        containing HTML tags
    :return: str
        where HTML tags got replaced with commas
    """
    return replace_tags(value, ', ')


def replace_nbsp(value: str) -> str:
    """Replaces non-breaking space characters (NBSP) with a space.
    Scrapy does not replace these by default.

    :param value: str
        containing NBSP characters
    :return: str
        where NBSP characters got replaced with spaces
    """
    return value.replace(u'\xa0', u' ')


class User(Item):
    name = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())


class Story(Item):
    title = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    summary = Field(input_processor=MapCompose(remove_tags, replace_escape_chars, replace_nbsp), output_processor=TakeFirst())
    status = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    likes = Field(input_processor=MapCompose(remove_tags, replace_escape_chars, replace_nbsp), output_processor=TakeFirst())
    follows = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    hits = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    storyCreatedAt = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    storyUpdatedAt = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    internalId = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    source = Field(output_processor=TakeFirst())
    category = Field(output_processor=TakeFirst())
    topics = Field(output_processor=TakeFirst())
    rating = Field(output_processor=TakeFirst())
    pairing = Field(output_processor=TakeFirst())
    genre = Field(input_processor=MapCompose(remove_tags, replace_escape_chars, replace_entities), output_processor=TakeFirst())
    fandom = Field(input_processor=MapCompose(remove_tags, replace_escape_chars, replace_entities), output_processor=TakeFirst())
    authorUrl = Field(output_processor=TakeFirst())
    characters = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=Join(', '))
