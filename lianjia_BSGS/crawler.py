import time
import re
import os
from multiprocessing.dummy import Pool as ThreadPool
import requests as rq
from pymongo import MongoClient
from .info import rent_type, city_info

TXT_PATH = "bc_lists.txt"


class Rent():
    def __init__(self):
        self.rent_type = rent_type
        self.city_info = city_info
        self.txt_path = TXT_PATH
        self.count = 0

        host = os.environ.get("MONGODB_HOST", "127.0.0.1")
        port = os.environ.get("MONGODB_PORT", "27017")
        mongo_url = "mongodb://{}:{}".format(host, port)
        mongo_db = os.environ.get("MONGODB_DB", "Lianjia")
        collection = "zufang"
        client = MongoClient(mongo_url)
        self.db = client[mongo_db]
        self.collections = self.db[collection]
        self.collections.create_index("m_url", unique=True)

    def _set_proxy(self):
        # 代理服务器
        proxyHost = "http-pro.abuyun.com"
        proxyPort = "9010"

        # 代理隧道验证信息
        # 注:已失效代理
        proxyUser = "HNZ7ZJ1T407D15RD"
        proxyPass = "271344D7826DB477"

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

        return proxies

    def get_data(self):
        for ty, type_code in self.rent_type.items():
            for city, info in self.city_info.items():
                for area, area_py in info[2].items():
                    url = "https://m.lianjia.com/chuzu/{}/zufang/{}/".format(info[1], area_py)
                    res_area = rq.get(url)
                    bc_lists = re.findall(r'data-type="bizcircle" data-key="(.*)" class="oneline ', res_area.text)
                    # print(bc_lists)
                    self._write_bc_list_to_text(bc_lists)
                    bc_lists = self._read_bc_list_from_text()
                    if bc_lists:
                        for bc_name in bc_lists:
                            index = 0
                            total = 1
                            while index * 30 <= total:
                                try:
                                    url = "https://app.api.lianjia.com/Rentplat/v1/house/list?city_id={}&condition={}/rt{}&limit=30&offset={}&request_ts={}&scene=list".format(
                                        info[0], bc_name, type_code, index * 30, int(time.time()))
                                    # urls.append(url)
                                    print(url)
                                    item = {"city": city, "type": ty, "area": area}
                                    # print(self._set_proxy())
                                    res = rq.get(url)
                                    if res.status_code == 200:
                                        print("正在爬取{}市{}区{}商圈的{}第{}页".format(city, area, bc_name, ty, index + 1))
                                        json_datas = res.json()
                                        self._parse_item(json_datas['data']['list'], item)
                                        total = json_datas['data']['total']
                                        index += 1

                                        # print("total {} index {}".format(total, index))
                                        if (total // 30) < index:
                                            break
                                    else:
                                        print("失败")
                                except Exception as e:
                                    print("连接不成功")
                                    print(e)

    def get_data_second(self, pool):
        print("enter")
        for ty, type_code in self.rent_type.items():
            for city, info in self.city_info.items():
                for area, area_py in info[2].items():
                    url = "https://m.lianjia.com/chuzu/{}/zufang/{}/".format(info[1], area_py)
                    res_area = rq.get(url)
                    bc_lists = re.findall(r'data-type="bizcircle" data-key="(.*)" class="oneline ', res_area.text)
                    # print(bc_lists)
                    self._write_bc_list_to_text(bc_lists)
                    bc_lists = self._read_bc_list_from_text()
                    if bc_lists:
                        item = {"city": city, "type": ty, "area": area}
                        for bc_name in bc_lists:
                            keywords = {"info": info[0], "bc_name": bc_name, "type_code": type_code, "ty": ty}
                            pool[0].apply_async(self._get_json, args=(item, keywords,))
                            # self._get_json(item, info=info[0], bc_name=bc_name, type_code=type_code, ty=ty)
                        pool[0].close()
                        pool[0].join()

    def _get_json(self, item, keywords):
        index = 0
        total = 1
        while index * 30 <= total:
            try:
                url = "https://app.api.lianjia.com/Rentplat/v1/house/list?city_id={}&condition={}/rt{}&limit=30&offset={}&request_ts={}&scene=list".format(
                    keywords['info'], keywords["bc_name"], keywords['type_code'], index * 30, int(time.time()))
                # urls.append(url)
                print(url)
                # print(self._set_proxy())
                res = rq.get(url)
                if res.status_code == 200:
                    print(
                        "正在爬取{}市{}区{}商圈的{}第{}页".format(item['city'], item['area'], keywords['bc_name'], keywords['ty'],
                                                       index + 1))
                    json_datas = res.json()
                    self._parse_item(json_datas['data']['list'], item)
                    total = json_datas['data']['total']
                    index += 1
                    # print("total {} index {}".format(total, index))
                    if (total // 30) < index:
                        break
                else:
                    print("失败")
            except Exception as e:
                print("连接不成功")
                print(e)

    def _parse_item(self, json_list, item):
        if json_list:
            for i in json_list:
                item['bedroom_num'] = i.get("frame_bedroom_num")
                item['hall_num'] = i.get('frame_hall_num')
                item['bathroom_num'] = i.get('frame_bathroom_num')
                item['rent_area'] = i.get('rent_area')
                item['house_title'] = i.get('house_title')
                item['resblock_name'] = i.get('resblock_name')
                item['bizcircle_name'] = i.get('bizcircle_name')
                item['layout'] = i.get('layout')
                item['rent_price_listing'] = i.get('rent_price_listing')
                item['house_tag'] = self._parse_house_tags(i.get('house_tags'))
                item['list_picture'] = i.get("list_picture")
                item['frame_orientation'] = i.get('frame_orientation')
                item['m_url'] = i.get('m_url')
                item['rent_price_unit'] = i.get('rent_price_unit')

                try:
                    res_murl = rq.get(item['m_url'], timeout=5)
                    item['longitude'] = re.findall(r"longitude: '(.*)',", res_murl.text)[0]
                    item['longitude'] = re.findall(r"latitude: '(.*)'", res_murl.text)[0]
                    flag = re.findall(r'<span class="fr">(\d+)米</span>', res_murl.text)
                    item['distance'] = flag and flag[0] or None

                except TimeoutError:
                    item['longitude'] = None
                    item['latitude'] = None
                    item['distance'] = None
                    print("获取经纬度与距离信息失败,m_url:{}".format(item['m_url']))

                self.collections.update_one({"m_url": item["m_url"]}, {"$set": item}, upsert=True)
                self.count += 1
                print("第{}条保存成功:{}".format(self.count, item))

    @staticmethod
    def _parse_house_tags(house_tags):
        if house_tags:
            tags = ""
            for tag in house_tags:
                tags += tag.get("name")
            return tags.strip()

    def _write_bc_list_to_text(self, bc_lists):
        with open(self.txt_path, 'w') as f:
            for bc_list in bc_lists:
                f.write(bc_list + "\n")

    def _read_bc_list_from_text(self):
        with open(self.txt_path, "r") as f:
            return [line.strip() for line in f.readlines()]


if __name__ == "__main__":
    p = ThreadPool(4)

    rent = Rent()
    rent.get_data_second([p])
