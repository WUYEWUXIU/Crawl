# %%
import re
import pandas as pd
import os
import sys
from urllib import request
from bs4 import BeautifulSoup


# 爬取存储到txt
URL = "http://www.stats.gov.cn/tjsj/zxfb/202201/t20220112_1826173.html"
req = request.Request(URL)
page = request.urlopen(req)
soup = BeautifulSoup(page, "html.parser")
page.close()

# %%
text = soup.get_text()
pattern = "('一、各类商品及服务价格同比变动情况')()('其他七大类价格同比六涨一降。')"
# pattern = "[,;.，；。]+[^,;.，；。]*影响CPI.*[,;.，；。]"
result = re.findall(pattern, text)
result
# print(result)
# %%
fp = open("Demo.txt", "w", encoding="utf-8")
tables = soup.findAll('table')
tab = tables[1]
trs = tab.findAll('tr')

for tr in trs:
    for td in tr.findAll('td'):
        text = td.getText() + ','
        fp.write(text.replace(' ', ''))
    fp.write('\n')
fp.close()

# %%
lines = [
    "起病以来,患者无腰背痛、颈痛,无咽痛、口腔溃疡,无光过敏、脱发,无口干、眼干,无肢端发作性青紫,无肢体乏力,无浮肿、泡沫尿,精神、食欲、睡眠欠佳,近1月大便干结,5-6天1次,无腹痛、黑便、便血,小便1-2小时1次,无尿痛、血尿。体重未见明显变化。",
    "起病以来,睡眠、胃纳正常,小便正常,近4~5年来每天解大便3~4次,多为黄褐色成形软便,偶有解烂便,有排便不尽感,便血、解黑便,无消瘦。",
    "身材矮小，体重较同龄人轻。"
]
for line in lines:
    pattern = "[,;.，；。]+[^,;.，；。]*[(小便)尿]+[^,;.，；。]*[,;.，；。]+"
    str = re.findall(pattern, line)
    print(str)
