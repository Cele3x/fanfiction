# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class User(Item):
    name = Field()


class Story(Item):
    title = Field()
    url = Field()
    summary = Field()
    status = Field()
    likes = Field()
    follows = Field()
    hits = Field()
    internalId = Field()
    categoryList = Field()
    sourceId = Field()
    author = User()
    genreId = Field()
    ratingId = Field()
    createdAt = Field()
    updatedAt = Field()
