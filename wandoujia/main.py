import requests as rq
from lxml import etree

headers={
  'Accept-Language': 'en',
  'Referer': 'https://www.wandoujia.com/category/',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  'Connection': 'keep-alive',
}

url="https://www.wandoujia.com/category/5029_716"

response=rq.get(url,headers=headers)
html=etree.HTML(response.text)
k=html.xpath('//li[1]//div[@class="comment"][1]/text()')[0]
k.strip()
print(str(k).strip())
print(k)
# for i in k:
#   print(i)

