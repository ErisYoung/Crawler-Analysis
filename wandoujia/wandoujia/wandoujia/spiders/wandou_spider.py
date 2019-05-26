# -*- coding: utf-8 -*-
from scrapy import Request
from wandoujia.items import WandoujiaItem
import scrapy
import re
from lxml import etree
from urllib.parse import urlencode
import json


class Get_category():
    def parse_category(self,response):
        html=etree.HTML(response.text)
        category_list=html.xpath('//li[@class="parent-cate"]')
        data=[{
            'cate_name':item.xpath(".//a/text()")[0],
            'cate_code':self.get_cate_code(item),
            'cate_child_code':self.get_child_cate(item),
        } for item in category_list]

        return data

    def get_cate_code(self,item):
        cate_url=item.xpath(".//a[@class='cate-link']/@href")[0]

        pattern=re.compile(r'.*/(\d+)')
        code=re.search(pattern,cate_url)
        return code.group(1)

    def get_child_cate(self,item):
        child_cate=item.xpath('.//div[@class="child-cate"]/a')
        # print(len(child_cate))
        child_cate_url=[{
            'child_cate_name':child.xpath('.//text()')[0],
            'child_cate_code':self.get_child_code(child),
        } for child in child_cate]
        # child_cate_url="1"
        return child_cate_url

    def get_child_code(self,child):
        child_cate_url=child.xpath(".//@href")[0]
        pattern = re.compile(r'.*_(\d+)')
        code = re.search(pattern, child_cate_url)
        return code.group(1)



class WandouSpiderSpider(scrapy.Spider):
    name = 'wandou_spider'
    # allowed_domains = ['wandoujia.com']
    def __init__(self):
        self.cate_url="https://www.wandoujia.com/category/app"
        self.url="https://www.wandoujia.com/category/"
        self.ajax_api="https://www.wandoujia.com/wdjweb/api/category/more?"

    def start_requests(self):
        yield Request(self.cate_url,callback=self.parse)

    def parse(self, response):
        cateGory=Get_category()
        content=cateGory.parse_category(response)
        # print(content)

        for item in content:
            child_cate=item['cate_child_code']
            for cate in child_cate:
                cate_code=item['cate_code']
                cate_name=item['cate_name']
                child_cate_code=cate['child_cate_code']
                child_cate_name=cate['child_cate_name']

                # page=1
                # if page==1:
                # category_url="{}{}_{}".format(self.url,cate_code,child_cate_code)
                # else:
                #     print("--------------------------------")
                page = 1
                params={
                        'catId':cate_code,
                        'subCatId':child_cate_code,
                        'page':page,
                }
                category_url=self.ajax_api+urlencode(params)
                dict={'page':page,'cate_name':cate_name,'cate_code':cate_code,'child_cate_name':child_cate_name,'child_cate_code':child_cate_code}
                yield Request(category_url,callback=self.recycle_parse,meta=dict)


    def recycle_parse(self,response):
        # content=etree.HTML(response.text)
        page=response.meta['page']
        if page<=10:
            cate_name=response.meta['cate_name']
            cate_code=response.meta['cate_code']
            child_cate_name=response.meta['child_cate_name']
            child_cate_code=response.meta['child_cate_code']

            jsonContent=json.loads(response.text)
            html=jsonContent['data']['content']
            selector=etree.HTML(html)

            for app in selector.xpath('//li[@class="card"]'):
                item=WandoujiaItem()
                item['cate_name']=cate_name
                item['child_cate_name'] =child_cate_name
                item['app_name'] =app.xpath(".//a[@class='name']/text()")[0]
                item['install'] =app.xpath('.//span[@class="install-count"]/text()')[0]
                item['volumn'] =app.xpath('.//span[3]/text()')[0]
                item['comments'] =str(app.xpath(".//div[@class='comment']/text()")[0]).strip()
                imgTemUrl=app.xpath(".//img/@src")[0]
                item['icon_url'] =str(imgTemUrl).startswith("http") and imgTemUrl or app.xpath(".//img/@data-original")[0]
                print(item)
                yield item

            page+=1
            params = {
                'catId': cate_code,
                'subCatId': child_cate_code,
                'page': page,
            }
            ajax_url=self.ajax_api+urlencode(params)

            dict = {'page': page, 'cate_name': cate_name, 'cate_code': cate_code, 'child_cate_name': child_cate_name,
                    'child_cate_code': child_cate_code}
            yield Request(ajax_url, callback=self.recycle_parse, meta=dict)
