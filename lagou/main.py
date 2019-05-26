import requests as rq
from fake_useragent import UserAgent
import time
import csv
import os
import pandas as pd
import requests


class lagou_spider(object):
    req_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
    url = 'https://www.baidu.com'
    ua = UserAgent()
    headers = {
        'Accept': 'application/json,text/javascript,*/*;q=0.01',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID=ABAAABAAAGGABCB10810748B022494A79A39F35C4C0EB7F; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1551336731; _ga=GA1.2.754172128.1551336731; _gid=GA1.2.1433337034.1551336731; user_trace_token=20190228145214-614894cb-3b25-11e9-8845-5254005c3644; LGSID=20190228145214-6148975d-3b25-11e9-8845-5254005c3644; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DC-fBh6th8h8QMkeByr31-b_C5GawNisN8sqVcBScbPO%26wd%3D%26eqid%3Dafae2fff000366f8000000065c778518%26ck%3D7134.3.94.352.248.257.142.541%26shh%3Dwww.baidu.com; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGUID=20190228145214-61489901-3b25-11e9-8845-5254005c3644; index_location_city=%E6%9D%AD%E5%B7%9E; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1551337835; LGRID=20190228151038-f33035fd-3b27-11e9-884f-5254005c3644; TG-TRACK-CODE=search_code; SEARCH_ID=e144d6b15b5a41b3b24e6339d2a98c',
        'Host': 'www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_Python?city=%E6%9D%AD%E5%B7%9E&cl=false&fromSearch=true&labelWords=&suginput=',
        'User-Agent': ua.random

    }
    page = 100
    save_path = "./lagou.csv"

    def file_to_csv(self, list_info):
        file_size = os.path.getsize(self.save_path)
        if file_size == 0:
            name = ['ID', '薪水', '学历要求', '工作经验']
            file_test = pd.DataFrame(columns=name, data=list_info)
            file_test.to_csv(self.save_path, encoding='gbk', index=False)
        else:
            with open(self.save_path, 'a+', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(list_info)

    def get_info(self):

        for i in range(1, self.page + 1):
            data = {
                'first': 'true',
                'kd': 'Python',
                'pn': i,
            }

            html = rq.post(self.req_url, data=data, headers=self.headers)
            html.encoding = 'utf-8'
            print('第%d页:' % i + str(html.status_code))

            req_info = html.json()

            print(req_info)
            req_info = req_info['content']['positionResult']['result']
            list_info = []

            for j in range(0, len(req_info)):
                salary = req_info[j]['salary']
                education = req_info[j]['education']
                workYear = req_info[j]['workYear']
                positionId = req_info[j]['positionId']
                list_one = [positionId, salary, education, workYear]
                list_info.append(list_one)
            print(list_info)

            self.file_to_csv(list_info)
            time.sleep(0.5)


lagou = lagou_spider()
lagou.get_info()
