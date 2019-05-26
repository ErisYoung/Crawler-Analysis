# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo as pm
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem

# class WandoujiaPipeline(object):
#     def process_item(self, item, spiders):
#         return item



class MongoPipeline(object):
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url=mongo_url
        self.mongo_db=mongo_db

    def open_spider(self, spider):
        self.client=pm.MongoClient(self.mongo_url)
        self.db=self.client[self.mongo_db]

    def close(self,spider):
        self.client.close()


    def process_item(self,item,spider):
        collectionName=item.__class__.__name__
        # 如相同则不插入
        self.db[collectionName].update_one(item,{'$set':item},upsert=True)
        return item


    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DB")
        )


class ImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['icon_url']:
            yield Request(item['icon_url'],meta={'item':item})


    def file_path(self, request, response=None, info=None):
        item=request.meta['item']
        name=item['app_name']
        cate_name=item['cate_name']
        child_cate_name=item['child_cate_name']
        path=r"{}/{}/{}.jpg".format(cate_name,child_cate_name,name)
        return path

    def item_completed(self, results, item, info):
        imagePaths=[path['path'] for x,path in results if x]
        if not imagePaths:
            raise DropItem("item contains no image")
        return item


