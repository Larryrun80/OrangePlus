#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: createcampaign.py

import re

import xlrd
import requests
import pypinyin


class Campaign(object):

    """docstring for Campaign"""

    def __init__(self, arg):
        super(Campaign, self).__init__()
        self.arg = arg


class CampaignBranch(object):

    """docstring for CampaignBranch"""

    def __init__(self, arg):
        super(CampaignBranch, self).__init__()
        self.arg = arg


class Brand:

    """docstring for Brand"""

    def __init__(self, arg):
        super(Brand, self).__init__()
        self.arg = arg


class Branch(object):

    """docstring for Branch"""

    def __init__(self, arg):
        super(Branch, self).__init__()
        self.arg = arg


class Item:

    """docstring for Item"""

    def __init__(self, **kwargs):
        self.brand_id = kwargs['brand_id']
        self.name = kwargs['name']
        if 'discription' in kwargs:
            self.description = kwargs['discription']
        if 'more_info' in kwargs:
            self.more_info = kwargs['more_info']
        if 'market_price' in kwargs:
            self.market_price = kwargs['market_price']


class OriginInfo:

    """docstring for OriginInfo"""

    def set_item_name(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v


def find_content(origin_string, key_name):
    # 本来可以用string.punctuation, 但牵涉到全角字符，还是自定义一个
    punctuation = [':', '：', ' ']
    pos = origin_string.find(key_name)
    if -1 != pos:
        pos = pos + len(key_name)

    while(origin_string[pos] in punctuation):
        pos = pos + 1

    return origin_string[pos:]

def get_info(file_name):
    data = xlrd.open_workbook(file_name)
    table = data.sheets()[0]
    row_count = table.nrows
    col_count = table.ncols

    # 定义所有需要的数据，用元组表示每一组数据
    # 第一个元素是用来存储数据的key，第二个是excel中的数据指示（需写全）
    # 第三个元素是需要处理为什么格式，''表示不需处理
    # 当前支撑的处理格式为: date, int, float
    contents = (
        ('brand_name', '商户名称（线上展示）', ''),
        ('campany_name', '公司名称（合同签约方）', ''),
        ('city', '所在城市', ''),
        ('brand_intro', '公司或品牌简介', ''),
        ('item_name', '商品名称', ''),
        ('market_price', '市场价格', 'float'),
        ('stock', '每日供应量', ''),
        ('start_time', '上线日期', 'date'),
        ('end_time', '下线日期', 'date'),
        ('item_intro', '商品详细描述（特色/成分/口感/功效等）', ''),
    )

    key_index = 0
    for i in range(row_count):
        for j in range(col_count):
            cell_value = str(table.cell(i, j).value).strip()
            if contents[key_index][1] in cell_value:
                value = find_content(cell_value, contents[key_index][1])
                if(contents[key_index][2] == 'date'):
                    value = '-'.join(re.findall('\d+', value))
                if(contents[key_index][2] == 'float'):
                    value = re.findall('\d*\.\d+|\d+', value)[0]
                print("%s: %s" % (contents[key_index][0], value))
                if key_index < len(contents) - 1:
                    key_index = key_index + 1

def get_branches(file_name, brand_name, city=None):
    data = xlrd.open_workbook(file_name)
    table = data.sheets()[0]
    row_count = table.nrows
    col_count = table.ncols

    branch_format = (
        'branch_name',
        'address',
        'phone',
        'mobile',
        'work_hour',
        'open_holiday',
        'redeem_type',
    )

    branch_row = 0
    for i in range(row_count):
        cell_value = str(table.cell(i, 0).value).strip()
        if '分店名称' in cell_value:
            branch_row = i + 1
            break

    branches = []
    offset = 0
    while table.cell(branch_row, col_count-1).value != '':
        offset = offset + 1
        branch = {}
        for i in range(len(branch_format)):
            branch[branch_format[i]] = table.cell(branch_row, i).value
        branch['phone'] = deal_phone_number(branch['phone'])
        branch['mobile'] = deal_phone_number(branch['mobile'])
        poi = get_lat_lng_using_address(branch['address'], city)
        branch['lng'] = poi[0]
        branch['lat'] = poi[1]
        branch_account = ''
        for j in range(len(brand_name)):
            branch_account += pypinyin.pinyin(brand_name[j], pypinyin.FIRST_LETTER)[0][0]
        branch['account'] = branch_account + str(offset)
        branches.append(branch)
        branch_row = branch_row + offset
    print(branches)

def get_lat_lng_using_address(address, city=None):
    request_url = 'http://apis.map.qq.com/ws/geocoder/v1'
    key = '3OUBZ-QW53G-Q5DQ4-I6RTL-UFK53-POFWA'
    request_url += '?address=' + address + '&key=' + key
    if city is not None:
        request_url += '&region=' + city

    try:
        response = requests.get(request_url, timeout=(5, 50)).json()
        if response['status'] != 0:
            return (0, 0)
        elif response['result']['deviation'] == -1:
            return (0, 0)
        else:
            return (response['result']['location']['lng'],
                    response['result']['location']['lat'],)
    except:
        return (0,0)

def deal_phone_number(value):
    # 如果是float类型， 取整
    if isinstance(value, float):
        value = str(int(value))
    # 如果是string类型， 取数字
    if isinstance(value, str):
        value = ''.join([i for i in value if i.isdigit()])

    # 如果不是手机号，且不是0开头， 加0
    if (len(value) != 11 or (len(value) == 11 and value[0] != '1')) and value[0] != '0':
        value = '0' + value
    return value

get_branches('abc.xls', '仙尚鲜')

# i = OriginInfo()
# i.set_item_name(brand_id=1)
# i.set_item_name(brand_id=4)
# print(i.__dict__)
# print(i.brand_id)

# data = xlrd.open_workbook('abc.xlsx')
# table = data.sheets()[0]
# row_count = table.nrows
# col_count = table.ncols
# for i in range(row_count):
#     for j in range(col_count):
#         cell_value = str(table.cell(i, j).value).strip()
#         if '商户名称' in cell_value:
#             pos = find_first_colon(cell_value)
#             if pos > 0:
#                 print(cell_value[pos+1:])
#             else:
#                 print(cell_value)

    # print(table.row_values(i))
    # print('--------------------------')
