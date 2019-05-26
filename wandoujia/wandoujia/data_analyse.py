import pandas as pd
from wordcloud import WordCloud
import json
from pyecharts import Bar, Scatter, Line, Page
import jieba as jb
from jieba.analyse import extract_tags
import pymongo as pm
import re

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = "wandoujia"
MONGO_TABLE = 'WandoujiaItem'
PATH = "wandoujia_app_detail.csv"

client = pm.MongoClient(MONGO_URI)
table = client[MONGO_DB][MONGO_TABLE]

datas = table.find({}, {'_id': 0})

df = pd.DataFrame(list(datas))
# print(df)
df.sort_values("cate_name", inplace=True)

df.reset_index(drop=True, inplace=True)

# df.to_csv(PATH,encoding="utf_8_sig",index=0)
# print(df)

pattern = re.compile(r'[\d.\w]+(?=人)')

for i in range(len(df.index)):
    install_str = str(df.loc[i, 'install'])
    count_str = re.search(pattern, install_str).group(0)
    if count_str[-1] == '亿':
        df.loc[i, 'install_count'] = int(float(count_str[:-1]) * 100000000)
    elif count_str[-1] == '万':
        df.loc[i, 'install_count'] = int(float(count_str[:-1]) * 10000)
    else:
        df.loc[i, 'install_count'] = int(count_str)

df.install_count = pd.to_numeric(df.install_count, downcast='integer', errors='ignore')

as_order_datas = df.sort_values('install_count', ascending=0).drop_duplicates(['app_name']).reset_index(drop=True)
most_ten = as_order_datas.head(10)

# print(most_ten.app_name.tolist())
'''下载量前10'''


def label_formatter(params):
    return params.value


page = Page()

bar = Bar("下载量最多的10个App")
bar.add('下载量',
        most_ten.app_name.tolist(),
        most_ten.install_count.tolist(),
        is_convert=True,
        xaxis_name="人次下载",
        )

page.add(bar)

'''cate_name 分类数目'''
df_type = df.cate_name.groupby(df['cate_name']).count()

line = Line('分类数目')
line.add(
    '数量',
    df_type.index.tolist(),
    df_type.values.tolist(),
    area_opacity=0.4,
    line_opacity=0.2,
)

page.add(line)

# print(as_order_datas.app_name.tolist())

datas = df.drop_duplicates(['app_name']).reset_index(drop=True)
'''scatter下载量图'''
scatter = Scatter('下载量图')
scatter.add('下载量',
            datas.app_name.tolist(),
            datas.install_count.tolist(),
            is_visualmap=True,

            xaxis_type="category",
            visual_range=[10, 300000000],
            is_datazoom_extra_show=True,
            datazoom_extra_type="slider",
            datazoom_extra_range=[0, 10000],
            yaxis_min=10,
            )

page.add(scatter)
page.render()

datas_comments = ':'.join(df['comments'].tolist())
frequents = extract_tags(datas_comments, withWeight=True, topK=50)

word = WordCloud(
    font_path=r"D:\s-data\note\pro\python\pratice\scrapy\bilibili_workcel\msyh.ttc",
    max_words=200,
    max_font_size=100,
    background_color='black',
    width=900,
    height=600,
)
word.generate_from_frequencies(dict(frequents))
word.to_file("comment_wandoujia_app.jpg")
