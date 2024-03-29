# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

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


def replace_tags_with_spaces(value: str) -> str:
    """Replaces tags with spaces.

    :param value: str
        containing tags
    :return: str
        where tags got replaced with spaces
    """
    return replace_tags(value, ' ')


def replace_multiple_spaces(value: str) -> str:
    """Replaces multiple spaces with just one.

    :param value: str
        containing spaces
    :return: str
        where multiple spaces got replaced with one
    """
    return re.sub(r'\s+', ' ', value)


def replace_escape_chars_with_spaces(value: str) -> str:
    """Replaces escape chars with spaces.

    :param value: str
        containing escape chars
    :return: str
        where escape chars got replaced with spaces
    """
    return replace_escape_chars(value, replace_by=' ')


DEFAULT_INPUT_PROCESSORS = MapCompose(replace_tags_with_spaces, replace_escape_chars, replace_entities, replace_nbsp, replace_multiple_spaces, str.strip)
TEXT_INPUT_PROCESSORS = MapCompose(replace_tags_with_spaces, replace_escape_chars_with_spaces, replace_entities, replace_nbsp, replace_multiple_spaces, str.strip)


class User(Item):
    username = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    url = Field(output_processor=TakeFirst())
    firstName = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    lastName = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    joinedOn = Field(output_processor=TakeFirst())
    locatedAt = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    country = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    gender = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    age = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    bio = Field(input_processor=TEXT_INPUT_PROCESSORS, output_processor=Join('\n'))
    source = Field(output_processor=TakeFirst())


class Story(Item):
    title = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    url = Field(output_processor=TakeFirst())
    summary = Field(input_processor=TEXT_INPUT_PROCESSORS, output_processor=Join('\n'))
    status = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    likes = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    follows = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    hits = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    publishedOn = Field(output_processor=TakeFirst())
    reviewedOn = Field(output_processor=TakeFirst())
    source = Field(output_processor=TakeFirst())
    category = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    topics = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    rating = Field(output_processor=TakeFirst())
    ratings = Field(input_processor=DEFAULT_INPUT_PROCESSORS)
    pairing = Field(output_processor=TakeFirst())
    pairings = Field(input_processor=DEFAULT_INPUT_PROCESSORS)
    genre = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=TakeFirst())
    fandom = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(' - '))
    fandoms = Field(input_processor=DEFAULT_INPUT_PROCESSORS)
    authorUrl = Field(output_processor=TakeFirst())
    characters = Field(input_processor=DEFAULT_INPUT_PROCESSORS)
    tags = Field(input_processor=DEFAULT_INPUT_PROCESSORS)
    ageVerification = Field(output_processor=TakeFirst())
    totalChapterCount = Field(output_processor=TakeFirst())
    totalReviewCount = Field(output_processor=TakeFirst())
    iid = Field(output_processor=TakeFirst())


class Chapter(Item):
    number = Field(output_processor=TakeFirst())
    title = Field(input_processor=DEFAULT_INPUT_PROCESSORS, output_processor=Join(', '))
    content = Field(input_processor=TEXT_INPUT_PROCESSORS, output_processor=Join('\n'))
    notes = Field(input_processor=TEXT_INPUT_PROCESSORS, output_processor=Join(', '))
    publishedOn = Field(output_processor=TakeFirst())
    reviewedOn = Field(output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    storyUrl = Field(output_processor=TakeFirst())


class Review(Item):
    url = Field(output_processor=TakeFirst())
    userUrl = Field(output_processor=TakeFirst())
    content = Field(input_processor=TEXT_INPUT_PROCESSORS, output_processor=Join(', '))
    reviewedAt = Field(output_processor=TakeFirst())
    reviewableType = Field(output_processor=TakeFirst())
    reviewableUrl = Field(output_processor=TakeFirst())
    parentUserUrl = Field(output_processor=TakeFirst())
    parentReviewedAt = Field(output_processor=TakeFirst())
    parentReviewableType = Field(output_processor=TakeFirst())
    parentReviewableUrl = Field(output_processor=TakeFirst())
    chapterNumber = Field(output_processor=TakeFirst())
    storyUrl = Field(output_processor=TakeFirst())
