import requests as rq
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import json
import time

url = 'https://bangumi.bilibili.com/review/web_api/short/list?media_id=102392&folded=0&page_size=20&sort=0'

headers = {
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Cookie": "LIVE_BUVID=AUTO8215218644834085; fts=1521864499; sid=9nsdl6kd; rpdid=kwqxpxkikqdosioqxpspw; im_notify_type_20612831=0; CURRENT_FNVAL=16; UM_distinctid=166d823e825461-0f5779decaf764-36664c08-144000-166d823e826385; stardustvideo=1; LIVE_PLAYER_TYPE=1; pgv_pvi=8327529472; buvid3=8F1AF37D-17CE-4D69-B5A8-5902AAEA4E5B77395infoc; CURRENT_QUALITY=80; finger=17c9e5f5; bp_t_offset_20612831=224812581277372703; DedeUserID=20612831; DedeUserID__ckMd5=956c2d2109ec3dea; SESSDATA=12e2bb9f%2C1554046817%2C92aad331; bili_jct=fbaa8d5223321fbbe34f978f8c3dcce2; _dfcaptcha=93c3642ac9fff720cd7d900886803810",
    "User-Agent": UserAgent(verify_ssl=False).random,
}

html = rq.get(url, headers=headers)
json_comment = json.loads(html.text)

total = json_comment['result']['total']
cols = ['cursor', 'author', 'mid', 'content', 'ctime', 'likes', 'score', 'final_watch']
data = pd.DataFrame(index=range(total), columns=cols)

i = 0
# 加速
total = total // 50
while i < total:
    n = len(json_comment['result']['list'])

    cursor = json_comment['result']['list'][n - 1]['cursor']

    for j in range(n):
        data.loc[i, 'cursor'] = cursor
        data.loc[i, 'author'] = json_comment['result']['list'][j]['author']['uname']
        data.loc[i, 'mid'] = json_comment['result']['list'][j]['author']['mid']
        data.loc[i, 'content'] = json_comment['result']['list'][j]['content']
        data.loc[i, 'ctime'] = json_comment['result']['list'][j]['ctime']
        data.loc[i, 'likes'] = json_comment['result']['list'][j]['likes']
        data.loc[i, 'score'] = json_comment['result']['list'][j]['user_rating']['score']
        try:
            data.loc[i, 'final_watch'] = json_comment['result']['list'][j]['user_season']['last_index_show']
        except:
            pass
        i += 1

    next_url = url + "&cursor=" + cursor
    json_comment = rq.get(next_url, headers=headers)
    json_comment = json.loads(json_comment.text)

    if i % 50 == 0:
        print("已经完成{}% ".format(round(i / total * 100, 2)))

    time.sleep(0.5)

data = data.fillna(0)


def getTime(x):
    gmtime_data = time.gmtime(x)
    return pd.Timestamp(gmtime_data[0], gmtime_data[1], gmtime_data[2], gmtime_data[3], gmtime_data[4], gmtime_data[5])


data['date'] = data.ctime.apply(lambda x: getTime(x))
data.to_csv("bili_workcell_short_comments.csv", index=False, encoding="utf_8_sig")
