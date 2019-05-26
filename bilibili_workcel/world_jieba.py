import jieba as jb
from jieba.analyse import extract_tags
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
from scipy.misc import imread

text=""
with open("31034.txt",'r',encoding='utf-8',errors='ignore') as f:
    text=f.read()

# methord1
# r=list(jb.cut(text))
# c=Counter(r)
# c_common=c.most_common(100)

# methord2
cut=" ".join(jb.cut(text))
r=extract_tags(cut,topK=100,withWeight=True)
# print(r)


# bg=imread('bg.jpg')
world=WordCloud(
    font_path="msyh.ttc",
    background_color="white",
    max_words=200,
    max_font_size=100,
    # mask=bg,
)

# world.generate(text)

# world.generate_from_frequencies(dict(c_common))

world.generate_from_frequencies(dict(r))

world.to_file("word_twice_extract.jpg")



