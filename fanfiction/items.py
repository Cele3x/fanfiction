# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags, replace_escape_chars

# ItemLoader.default_input_processor = MapCompose(remove_tags, replace_escape_chars)
# ItemLoader.default_outut_processor = TakeFirst()


class User(Item):
    name = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    createdAt = Field(output_processor=TakeFirst())
    updatedAt = Field(output_processor=TakeFirst())


class Story(Item):
    title = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    summary = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    status = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    likes = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    follows = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    hits = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    storyCreatedAt = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    storyUpdatedAt = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    internalId = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    categoryList = Field(output_processor=Join())
    sourceId = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    authorUrl = Field(output_processor=TakeFirst())
    genreId = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    ratingId = Field(input_processor=MapCompose(remove_tags, replace_escape_chars), output_processor=TakeFirst())
    createdAt = Field(output_processor=TakeFirst())
    updatedAt = Field(output_processor=TakeFirst())
