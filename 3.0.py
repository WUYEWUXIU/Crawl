# %%
from treelib import Tree
import sys
from numpy import NAN
import pandas as pd
import requests
import re
from lxml import etree
from styleframe import StyleFrame


date = sys.argv[1]
url = sys.argv[2]
# 测试集url和enddate
# date = '20220113'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202011/t20201110_1800180.html'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202010/t20201015_1794072.html'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202009/t20200909_1788414.html'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202112/t20211209_1825133.html'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202201/t20220112_1826173.html'
# url = 'http://www.stats.gov.cn/tjsj/zxfb/202110/t20211014_1822870.html'
response = requests.get(url).content.decode()

# 爬
html = etree.HTML(response)
data = ''.join(html.xpath('//p[@class="MsoNormal"]//text()'))
r_1 = re.compile('.*?各类商品及服务价格同比变动情况(.*?)其他七大类价格.*?', re.S)
r_2 = re.compile('.*?各类商品及服务价格环比变动情况(.*?)其他七大类价格.*?', re.S)
info_1 = re.findall(r_1, data)
info_2 = re.findall(r_2, data)
R_1 = re.compile('(.*?)；', re.S)
yoy = re.findall(R_1, info_1[0].replace('。', '；').replace(
    '其中', '；').replace('食品中', '').replace('CPI', ''))
mom = re.findall(R_1, info_2[0].replace('。', '；').replace(
    '其中', '；').replace('食品中', '').replace('CPI', ''))

# 读取模板
ref = pd.read_excel('NBSC_CPI_GXBFD.XLSX', sheet_name=['YOY', 'MOM'])
ref_yoy = ref['YOY']
ref_yoy.drop([0, 1, 17], inplace=True)
ref_mom = ref['MOM']
ref_mom.drop([0, 1, 17], inplace=True)


def filter(x, pattern):
    if pattern == 'yoy':
        sens = yoy
    else:
        sens = mom
    if len(x) - 1:
        for sen in sens:
            if x[1] in sen:
                if x[0] in sen:
                    if '上涨' in sen:
                        return [True, x[0], float(re.findall(r'[0-9.]+', sen)[-1])]
                    elif '下降' in sen:
                        return [True, x[0], - float(re.findall(r'[0-9.]+', sen)[-1])]
                    else:
                        return 10000
                else:
                    if '上涨' in sen:
                        return [True, x[1], float(re.findall(r'[0-9.]+', sen)[-1])]
                    elif '下降' in sen:
                        return [True, x[1], - float(re.findall(r'[0-9.]+', sen)[-1])]
                    else:
                        return 10000
    else:
        for sen in sens:
            if x[0] in sen:
                if '上涨' in sen:
                    return [True, x[0], float(re.findall(r'[0-9.]+', sen)[-1])]
                if '下降' in sen:
                    return [True, x[0], - float(re.findall(r'[0-9.]+', sen)[-1])]
                else:
                    return 10000
    return [False, '', NAN]


node_list_yoy_parse = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x))
node_list_yoy = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x)[-2:])
node_list_yoy_bool = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x)[-2:]).apply(filter, args=['yoy'])
node_list_mom_parse = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x))
node_list_mom = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x)[-2:])
node_list_mom_bool = ref_yoy['data_name'].apply(lambda x: re.findall(
    '(.*?):', x)[-2:]).apply(filter, args=['mom'])

node_list_yoy_name = node_list_yoy[node_list_yoy_bool.apply(lambda x: x[0])]
node_list_mom_name = node_list_mom[node_list_mom_bool.apply(lambda x: x[0])]
node_list_yoy_name = node_list_yoy_bool[node_list_yoy_name.index].apply(
    lambda x: x[1]).drop_duplicates(keep='first')
node_list_mom_name = node_list_yoy_bool[node_list_yoy_name.index].apply(
    lambda x: x[1]).drop_duplicates(keep='first')
node_list_yoy_val = node_list_yoy_bool[node_list_yoy_name.index].apply(
    lambda x: x[2]).drop_duplicates(keep='first')
node_list_mom_val = node_list_mom_bool[node_list_mom_name.index].apply(
    lambda x: x[2]).drop_duplicates(keep='first')


# yoy
yoy_df = ref_yoy.loc[node_list_yoy_val.index]
yoy_df['val'] = node_list_yoy_val

# mom
mom_df = ref_mom.loc[node_list_mom_val.index]
mom_df['val'] = node_list_mom_val

print(mom_df, '\n', yoy_df)

# output
path = date + '.xlsx'
writer = StyleFrame.ExcelWriter(path)

yoy_sf = StyleFrame(yoy_df)
yoy_sf.to_excel(
    excel_writer=writer,
    sheet_name='YOY',
    best_fit=yoy_df.columns.tolist(),
    allow_protection=True,
)

mom_sf = StyleFrame(mom_df)
mom_sf.to_excel(
    excel_writer=writer,
    sheet_name='MOM',
    best_fit=mom_df.columns.tolist(),
    allow_protection=True,
)

writer.save()
