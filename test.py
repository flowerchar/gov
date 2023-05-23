# # from wordcloud import  WordCloud
# # s1 = {'贵阳': 147, '遵义': 16, '六盘水': 59, '贵安': 35, '贵州': 49, "石阡":0}
# #
# # w1 = WordCloud(font_path=r'C:\Windows\Fonts\STXINWEI.TTF',
# #                        background_color='white', width=1600, height=800, collocations=False).generate_from_frequencies(s1)
# # w1.to_file("test.png")
#
import requests
from lxml import etree

url = 'https://www.bilibili.com/video/BV1Sv41117KQ/?spm_id_from=333.337.search-card.all.click&vd_source=fdf7f8680f50e1bd5a56f2dcb60b0360'
resp = requests.get(url=url)
resp.encoding = resp.apparent_encoding
tree = etree.HTML(resp.text)
print(resp.text)

# up主，
# up主粉丝量
