from pyecharts import Pie, Line, Page, Scatter
import pandas as pd
from enum import Enum
import numpy as np
from wordcloud import WordCloud
import jieba as jb
from jieba.analyse import extract_tags
from collections import Counter
from scipy.misc import imread

datas = pd.read_csv('bili_workcell_short_comments.csv')

# 筛选有效行
effect_datas = -1
for i in range(datas.shape[0]):
    if datas.loc[i, "mid"] == 0:
        effect_datas = i
        break

datas = datas.head(effect_datas)

"""评分饼图"""

scores = datas.score.groupby(datas['score']).count()

# 处理当前数据中不存在的属性
star = [2, 4, 6, 8, 10]
index = list(scores.index)
values = list(scores.values)
for i in star:
    if i not in scores.index:
        j = int(i / 2 - 1)
        index.insert(j, 2)
        values.insert(j, 0)

page = Page()

pie = Pie('评分饼图', title_pos="center", width=900)
pie.add("评分",
        ['一星', '两星', '三星', '四星', '五星'],
        values,
        radius=[30, 75],
        is_random=True,
        is_label_show=True,
        legend_pos="10%",
        legend_orient="vertical",
        )

page.add(pie)

"""评论时间分布"""

# 保留当天时间
datas['dates'] = datas.date.apply(lambda x: pd.Timestamp(x).date())

sum = datas.score.groupby(datas['dates']).sum()
count = datas.score.groupby(datas['dates']).count()

index_per_day = list(sum.index)
values_per_day = list(sum / count)
values_per_day = [int(x) for x in values_per_day]

chart = Line("评分时间分布")
chart.use_theme("dark")

chart.add("评分",
          index_per_day,
          values_per_day,
          )

page.add(chart)

"""每日评论数目"""

chart2 = Line("评论数时间分布")
chart2.use_theme("dark")
chart2.add("评论数", index_per_day, list(count.values), line_opacity=0.2,
           area_opacity=0.4, symbol=None)

page.add(chart2)

"""好评字数分布"""

dataLikes = datas[datas.likes >= 1]
# print(dataLikes.likes)

dataLikes['comment_length'] = dataLikes.content.apply(lambda x: len(x))

chart3 = Scatter("好评字数分布")
chart3.add("likes", dataLikes.comment_length, dataLikes.likes,
           is_visualmap=True,
           xaxis_name="评论字数",
           )

page.add(chart3)

"""评论日内分布"""


def label_formatter(params):
    return params.value[0] + "时:" + params.value[1] + "评论"


datas['time_hour'] = datas.date.apply(lambda x: pd.Timestamp(x).hour)

num_hour = datas.score.groupby(datas['time_hour']).count()

chart4 = Line("评论日内分布")
chart4.use_theme("dark")
chart4.add("评论数", num_hour.index.values, list(num_hour.values),
           line_width=2,
           is_label_show=True,
           mark_point_symbol="diamond",
           label_formatter=label_formatter,
           label_text_size=10,
           )

page.add(chart4)

page.render()

"""分词"""

text = ';'.join(datas.content.tolist())
"""分词两次无差别"""
# text_cut=" ".join(jb.cut(text))
text_frequence = extract_tags(text, topK=50, withWeight=True)

world = WordCloud(
    font_path="msyh.ttc",
    max_font_size=100,
    max_words=100,
    background_color="black",
    # mask=path,
)

world.generate_from_frequencies(dict(text_frequence))

world.to_file("bili_comment_worldCloud_twice.jpg")
