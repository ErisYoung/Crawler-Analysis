from pyecharts import Bar, Line, Scatter, Pie, Page
from wordcloud import WordCloud
from matplotlib.pyplot import plot
import pandas as pd
import jieba as jb
from jieba.analyse import extract_tags

datas = pd.read_csv("xiamu_comment_douban_csv.csv", encoding="utf_8_sig")

# 筛选出star为digit的行，过滤错误信息
datas = datas[[str(i).isdigit() for i in datas.star]]

# print(datas.star)
star = datas.star.groupby(datas['star']).count()
# print(star.values)
page = Page()
# 评分饼图
pie = Pie("评分饼图", title_pos="center", width=900)
pie.add("评分",
        ['未评分', '一星', '两星', '三星', '四星', '五星'],
        star.values.tolist(),
        is_random=True,
        radius=[30, 75],
        is_label_show=True,
        legend_pos="10%",
        legend_top="center",
        legend_orient="vertical",
        )

page.add(pie)

# 每日平均评分

# 筛选出不为0的行
datas = datas[[int(i) > 0 for i in datas.star]]
datas.star = datas.star.astype(int)

datas["timeT"] = datas.time.apply(lambda x: pd.Timestamp(x).date())

sum = datas.star.groupby(datas['timeT']).sum()
count = datas.star.groupby(datas['timeT']).count()
per_day = sum / count
per_day_list = [int(i) for i in per_day.values]
date_list = sum.index.tolist()

line = Line("每日平均评分")
line.use_theme("dark")
line.add("评分",
         date_list,
         per_day_list,
         )

page.add(line)

"每日评论数目"
line2 = Line('每日评论数目')
line2.add("数目",
          date_list,
          sum.values.tolist(),
          area_opacity=0.4,
          line_opacity=0.2,
          )
page.add(line2)

"评论时刻"

datas['comment_hour'] = datas.time.apply(lambda x: pd.Timestamp(x).hour)

hour_count = datas.star.groupby(datas['comment_hour']).count()


# print(hour_count)
def print_tooltip(params):
    return params.value[0] + "时" + params.value[1] + "评论数"


scatter = Scatter("评论时刻")
scatter.add("评论日内分析",
            hour_count.index,
            hour_count.values,
            is_visualmap=True,
            xaxis_name="评论时刻",
            tooltip_formatter=print_tooltip,
            xaxis_force_interval=1,
            )

page.add(scatter)

page.render()

comments = " ".join(datas.content.tolist())
comments_frequents = extract_tags(comments, topK=50, withWeight=True)

wc = WordCloud(
    font_path=r"D:\s-data\note\pro\python\pratice\scrapy\bilibili_workcel\msyh.ttc",
    max_font_size=100,
    max_words=100,
    background_color="black",
)

wc.generate_from_frequencies(dict(comments_frequents))
wc.to_file("xiamu_wordcloud.jpg")
