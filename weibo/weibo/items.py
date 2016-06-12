# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field


class fanItem(Item):
    user_id = Field()
    fan_id = Field()
    fan_name = Field()

class weiboItem(Item):
    user_id = Field()
    content = Field()
    time = Field()
    weibo_id = Field()

class commentItem(Item):
    user_id = Field()
    weibo_id = Field()
    comment_id = Field()
    content = Field()
    time = Field()
