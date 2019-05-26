# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class WandoujiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    cate_name=Field()
    child_cate_name = Field()
    app_name= Field()
    install = Field()
    volumn = Field()
    comments = Field()
    icon_url = Field()

