import requests as rq
from bs4 import BeautifulSoup
from lxml import etree
import pandas
from collections import Counter
import pandas as pd
import numpy as np
import time
from fake_useragent import UserAgent
import re
import time
import random

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "HD7P8515EC6M1BRD"
proxyPass = "EE68302525980008"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}


def get_proxy():
    with open('../ipproxy/proxies_https.txt', 'r') as f:
        proxies_data = f.readlines()
        proxy_one = random.choice(proxies_data).strip()
        return {proxy_one.split(":")[0]: proxy_one}


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Host": "movie.douban.com",
    "Referer": "https://movie.douban.com/",
    "User-Agent": UserAgent(verify_ssl=False).random,
}

url = "https://movie.douban.com/subject/27166442/comments?start={}&limit=20&sort=new_score&status=P&percent_type="


cols = ['username', 'star', 'time', 'content', 'img_url']

page_num, foot_num = 50, 2
path = 'xiamu_comment_douban_csv.csv'

datas = pd.DataFrame(columns=cols)

i = 0
while True:
    parseUrl = url.format(i * 20)
    print(proxies)
    html = rq.get(parseUrl, headers=headers, proxies=proxies)
    print("当前状态:%s" % html.status_code)
    html.encoding = 'utf-8'

    selector = etree.HTML(html.text)

    boxes = selector.xpath('//div[@id="comments"]//div[@class="comment-item"]')
    items_num = len(boxes)

    print("当前第%d页,存在%d条" % (i, items_num))
    # print(items_num)
    data_one_page = pd.DataFrame(index=range(items_num), columns=cols)

    for k, box in enumerate(boxes):

        data_one_page.loc[k, "username"] = box.xpath('.//span[@class="comment-info"]//a/text()')[0]

        star = box.xpath('.//span[@class="comment-info"]//span[contains(@class,"rating")]/@class')
        if len(star) == 0:
            s = 0
        else:
            s = re.search(r'\d', star[0]).group(0)
        data_one_page.loc[k, "star"] = int(s)

        data_one_page.loc[k, 'time'] = box.xpath('.//span[@class="comment-info"]//span[@class="comment-time "]/@title')[
            0]
        data_one_page.loc[k, 'content'] = box.xpath('.//p/span/text()')[0].strip()
        data_one_page.loc[k, 'img_url'] = box.xpath('.//div[@class="avatar"]//a/img/@src')[0]

        time.sleep(0.1)

    headersFlag = i == 0 and True or False

    with open(path, 'a+', encoding='utf_8_sig') as f:
        if i != 0:
            print(i)
            f.write("\n")
        data_one_page.to_csv(path_or_buf=f, index=0, encoding="utf_8_sig", header=headersFlag)

    i += 1

    datas = pd.concat([datas, data_one_page], ignore_index=True)

    # 判断是否还要下页
    next = boxes[0].xpath('..//div[@id="paginator"]/a[@class="next"]')
    if len(next) == 0:
        break

    time.sleep(0.2)
