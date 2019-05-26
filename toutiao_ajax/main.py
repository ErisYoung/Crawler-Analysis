import time
import math
import os
from multiprocessing import Pool
from hashlib import md5
import requests as rq
from urllib.parse import urlencode




def __init__(self):
        self.aid=24
        self.app_name='web_search'
        self.format="json"
        self.keyword="杭州"
        self.autoload='true'
        self.count="20"
        self.en_qc='1'
        self.cur_tab='1'
        self._from='search_tab'
        self.pd='synthesis'
        self.timestamp= math.ceil(time.time()*1000)


def get_page(offset):
    params={
        'aid':'24',
        'app_name':'web_search',
        'offset':offset,
        'format':'json',
        'keyword':'街拍图集',
        'autoload':'true',
        'count':'20',
        'en_qc':'1',
        'cur_tab':'1',
        'from':'search_tab',
        'pd':'synthesis',
        'timestamp':math.ceil(time.time()*1000),
    }

    url="https://www.toutiao.com/api/search/content/?"+urlencode(params)
    print('url:',url)
    try:
        response=rq.get(url)
        if response.status_code==200:
            return response.json()
    except rq.ConnectionError:
        return None

def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            if 'abstract' in item:
                title=item.get('title')
                images=item.get('image_list')
                for image in images:
                    yield {
                        'url':image.get('url'),
                        'title':title,
                    }


def save_image(item,path_root="imgs/"):
    folder_path=item.get('title')
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    try:
        response=rq.get(item.get('url'))
        if response.status_code==200:
            file_path="{}/{}.{}".format(folder_path,md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print("image exists")

    except rq.ConnectionError:
        print("Fail to save")



def main(offset):
    json=get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START=1
GROUP_END=20
if __name__=="__main__":
    pool=Pool()
    groups=[i*20 for i in range(GROUP_START,GROUP_END+1)]
    pool.map(main,groups)
    pool.close()
    pool.join()







