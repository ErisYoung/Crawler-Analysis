import requests as rq
import pandas as pd
from lxml import etree
import json
import datetime
import time as tm
import numpy as np

import pyecharts as pc

import os

from fake_useragent import UserAgent

api = 'http://www.cbooo.cn/BoxOffice/getCBW?pIndex={}&dt={}'

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Connection': 'keep-alive',
    'Cookie': 'Hm_lvt_bfc6c23974fbad0bbfed25f88a973fb0=1549370898; bdshare_firstime=1549370902439; Hm_lvt_daabace29afa1e8193c0e3000d391562=1549853629,1550066364,1550111083,1551498886; Hm_lpvt_daabace29afa1e8193c0e3000d391562=1551499055',
    'Host': 'www.cbooo.cn',
    'Referer': 'http://www.cbooo.cn/cinemaweek',
    'User-Agent': UserAgent(verify_ssl=False).random}

columns = ['cinemaName', 'amount', 'avgPS', 'avgScreen', 'screen_yield', 'scenes_time']

page = 1


def get_page_info(time):
    datafl = pd.DataFrame()
    for i in range(1, page + 1):
        # print(api.format(i, time))
        resp = rq.get(api.format(i, time), headers=headers)
        html = resp.text
        resp_json = json.loads(html)

        n = len(resp_json['data1'])

        datas = pd.DataFrame(index=range(n), columns=columns)

        for j in range(n):
            datas.loc[j, 'cinemaName'] = resp_json['data1'][j]['cinemaName']
            datas.loc[j, 'amount'] = resp_json['data1'][j]['amount']
            datas.loc[j, 'avgPS'] = resp_json['data1'][j]['avgPS']
            datas.loc[j, 'avgScreen'] = resp_json['data1'][j]['avgScreen']
            datas.loc[j, 'scenes_time'] = resp_json['data1'][j]['scenes_time']
            datas.loc[j, 'screen_yield'] = resp_json['data1'][j]['screen_yield']

        datafl = pd.concat([datafl, datas], axis=0)

        print("已经完成{}% ！".format(round(i / page)))
        tm.sleep(0.5)

        datafl = datafl.reset_index()
        print(datafl['amount'])
        return datafl


def parse_data(data1, data2):
    data1.drop_duplicates()
    data2.drop_duplicates()

    datas = pd.merge(data1, data2, left_on=['cinemaName'], right_on=['cinemaName']).dropna()

    datas.reset_index(drop=True)

    datafl = datas[['cinemaName']]

    datafl['amount'] = datas['amount_x'].astype(float) + datas['amount_y'].astype(float)
    datafl['avgPS'] = (datas['avgPS_x'].astype(float) + datas['avgPS_y'].astype(float)) / 2
    datafl['avgScreen'] = datas['avgScreen_x'].astype(float) + datas['avgScreen_y'].astype(float)

    datafl['screen_yield'] = (datas['screen_yield_x'].astype(float) + datas['screen_yield_y'].astype(float)) / 2
    datafl['scenes_time'] = (datas['scenes_time_x'].astype(float) + datas['scenes_time_y'].astype(float)) / 2
    datafl['avgprice'] = datafl.screen_yield / datafl.scenes_time / datafl.avgPS

    datafl = datafl.dropna().reset_index(drop=True)
    return datafl


def print_scatter(datas):
    style = pc.Style().add(
        is_visualmap=True,
        xaxis_name="平均票价",
        yaxis_name="场均人次",
        tooltip_formatter="{c}"
    )
    sc = pc.Scatter('test', 'subtest')

    datas_amount = datas.amount.values
    datas_avgPS = datas.avgPS.astype(float).round(1)
    datas_avgprice = datas.avgprice.astype(float).round(1)

    sc.add("test", datas_avgprice, datas_avgPS, extra_data=list(datas_amount), **style)

    sc.render("test.html")


if __name__ == "__main__":
    data1=get_page_info(1040)
    data2=get_page_info(1041)
    datafl=parse_data(data1,data2)

    path = "piaofan_from_cnboo.csv"

    if os.path.exists("piaofan_from_cnboo.csv"):
        datas = pd.read_csv(path, index_col=0)
        print_scatter(datas)

    else:
        pass
        datafl.to_csv(path, encoding="utf_8_sig")
