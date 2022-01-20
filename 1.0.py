# %%
from bisect import bisect_left
import pandas as pd
import os
import sys
from urllib import request
from bs4 import BeautifulSoup
# urllib.request.urlopen
# main()
# if len(sys.argv) ==2:
#     n = int(sys.argv[1])
# else:
#     print('usage: get_pl5.py n ')
#     sys.exit(1)

# 爬取存储到txt
URL = "http://www.stats.gov.cn/tjsj/zxfb/202201/t20220112_1826173.html"
req = request.Request(URL)
page = request.urlopen(req)
soup = BeautifulSoup(page, "html.parser")
page.close()

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

# 读取保存的txt
data = pd.read_csv('Demo.txt', sep=',', usecols=[0, 1, 2, 3])

# 分成4级标题，其中0级标题只可能是第一种
class_0_loc = [0]
class_1_loc = []
class_1_loc_2 = []
class_2_loc = []
class_3_loc = []

# 将所有1级标题和3级标题的位置筛选出来
for i in range(data.shape[0]):
    str = data.iloc[:, 0][i]
    if all([x in str for x in ['其中', '食品']]) and (not any([x in str for x in ['能源']])):
        class_1_loc_2.append(i)
    if any([x in str for x in ['非食品']]):
        class_1_loc_2.append(i)
    if any([x in str for x in ['一', '二', '三', '四', '五', '六', '七', '八']]):
        class_1_loc.append(i)
    if any([x in str for x in ['猪', '牛', '羊']]):
        class_3_loc.append(i)

# 将所有2级标题的位置筛选出来
for i in range(class_1_loc[0], class_1_loc[-1]+1):
    if (i not in class_1_loc) and (i not in class_3_loc):
        class_2_loc.append(i)

# 如果是0级标题的话，就单纯是CPI即可
for i in class_0_loc:
    data.iloc[i, 0] = 'CPI'

# 如果是1级标题的话，就需要在0级标题的基础上再加上1级标题
for i in class_1_loc:
    data.iloc[i, 0] = 'CPI:' + data.iloc[i, 0][2:]

for i in class_1_loc_2:
    b = data.iloc[i, 0].split()
    c = "".join(b)
    if '其中：' in c:
        c = c[3:]
    data.iloc[i, 0] = 'CPI:' + c

# 如果是2级标题的话，就需要在1级标题的基础上再加上2级标题
for i in class_2_loc:
    b = data.iloc[i, 0].split()
    c = "".join(b)
    last_first_class = class_1_loc[bisect_left(class_1_loc, i)-1]
    data.iloc[i, 0] = data.iloc[last_first_class, 0] + ':' + c

# 如果是3级标题的话，就需要在2级标题的基础上再加上3级标题
for i in class_3_loc:
    b = data.iloc[i, 0].split()
    c = "".join(b)
    if '其中：' in c:
        c = c[3:]
    last_second_class = class_1_loc[bisect_left(class_2_loc, i)-1]
    data.iloc[i, 0] = data.iloc[last_first_class, 0] + ':' + c

# 如果每一个类别都不是，直接删掉
no_class = []
for i in range(data.shape[0]):
    if i not in class_0_loc:
        if i not in class_1_loc:
            if i not in class_1_loc_2:
                if i not in class_2_loc:
                    if i not in class_3_loc:
                        no_class.append(i)
data.drop(no_class, inplace=True)

# 加上同比和环比

yoy = pd.DataFrame()
mom = pd.DataFrame()

yoy['data_name'] = data.iloc[:, 0].apply(lambda x: x + ':当月同比')
yoy['val'] = data.iloc[:, 2]

mom['data_name'] = data.iloc[:, 0].apply(lambda x: x + ':当月环比')
mom['val'] = data.iloc[:, 1]
