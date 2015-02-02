#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: createcampaign.py

import re
import time
import os

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

    def set_attributes(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v


def find_content(origin_string, key_name):

    '''
        从一个cell中过滤掉提示文字，或许需要的内容
    '''

    # 本来可以用string.punctuation, 但牵涉到全角字符，还是自定义一个
    punctuation = [':', '：', ' ']
    # 找到提示位置的结束位置
    pos = origin_string.find(key_name)
    if -1 != pos:
        pos = pos + len(key_name)
    # 过滤掉可能的异常字符
    while(origin_string[pos] in punctuation):
        pos = pos + 1

    return origin_string[pos:]


def get_info(file_name):

    '''
        从excel获取非门店以外的所有信息
    '''

    data = xlrd.open_workbook(file_name)
    table = data.sheets()[0]
    row_count = table.nrows
    col_count = table.ncols

    # 定义所有需要的数据，用元组表示每一组数据
    # 第一个元素是用来存储数据的key，第二个是excel中的数据指示（需写全）
    # 第三个元素是需要处理为什么格式，''表示不需处理
    # 当前支撑的处理格式为: date, int, float
    # 遍历的时候为了节省资源，是在一次遍历中获取所有数据，获取到一个数据后在剩余cell查找下一个，所以需要保证content中的顺序符合先左后右先上后下的原则
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

    result = {}
    # key_index 是内容下标，读取到一个值后移动到下一个需要读取的值
    key_index = 0
    for i in range(row_count):
        for j in range(col_count):
            cell_value = str(table.cell(i, j).value).strip()
            # 如果含有对应的指示文字
            if contents[key_index][1] in cell_value:
                value = find_content(cell_value, contents[key_index][1])
                # 对日期类型，提取所有数字并加上-， 形成yyyy-mm-dd格式
                if(contents[key_index][2] == 'date'):
                    value = '-'.join(re.findall('\d+', value))
                # 对价格部分， 从字符串中提取整数或浮点数
                if(contents[key_index][2] == 'float'):
                    value = re.findall('\d*\.\d+|\d+', value)[0]
                result[contents[key_index][0]] = value
                if key_index < len(contents) - 1:
                    key_index = key_index + 1
    return result


def get_branches(file_name, brand_name, city=None):

    '''
        从excel获取所有门店信息
    '''

    # brand_name是否包含中文
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    if not os.path.exists(file_name) or brand_name is None or not zhPattern.search(brand_name):
        return None

    data = xlrd.open_workbook(file_name)
    table = data.sheets()[0]
    row_count = table.nrows
    col_count = table.ncols

    # 这里的定义和excel中门店信息的列严格保持一致
    branch_format = (
        'branch_name',
        'address',
        'phone',
        'mobile',
        'work_hour',
        'open_holiday',
        'redeem_type',
    )

    # branch_row定义了从哪一行开始门店数据
    branch_row = 0
    for i in range(row_count):
        cell_value = str(table.cell(i, 0).value).strip()
        if '分店名称' in cell_value:
            branch_row = i + 1
            break

    branches = [] # 用于存储处理好的门店
    offset = 0 # offset 在创建门店账号时提供后缀
    # 如果某一行最后一列的值为空，代表着这行不是门店信息了
    while table.cell(branch_row, col_count-1).value != '':
        offset = offset + 1
        branch = {}
        # 遍历存储某个门店的全部信息
        for i in range(len(branch_format)):
            branch[branch_format[i]] = table.cell(branch_row, i).value
        # 格式化电话和手机
        branch['phone'] = deal_phone_number(branch['phone'])
        branch['mobile'] = deal_phone_number(branch['mobile'])
        # 格式化验证方式
        branch['redeem_type'] = deal_redeem_type(branch['redeem_type'])
        # 通过地址和城市获取门店的位置坐标，获取失败返回（0，0）
        poi = get_lat_lng_using_address(branch['address'], city)
        branch['lng'] = poi[0]
        branch['lat'] = poi[1]
        # 开始生成登陆账号、密码
        # 账号的生成规则为拼音首字母
        branch_account = ''
        for j in range(len(brand_name)):
            branch_account += pypinyin.pinyin(brand_name[j], pypinyin.FIRST_LETTER)[0][0]
        branch['account'] = branch_account + str(offset)
        branch['password'] = time.strftime('%y%m%d',time.localtime(time.time()))
        # 添加到branches
        branches.append(branch)
        branch_row = branch_row + offset
    return branches


def get_lat_lng_using_address(address, city=None):

    '''
        通过地址文字获取坐标
        调用soso地图API
        如果获取失败，返回(0, 0)
    '''

    request_url = 'http://apis.map.qq.com/ws/geocoder/v1'
    key = '3OUBZ-QW53G-Q5DQ4-I6RTL-UFK53-POFWA' # soso的开发者key
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
    if len(value) > 0 and (len(value) != 11 or (len(value) == 11 and value[0] != '1')) and value[0] != '0':
        value = '0' + value
    return value


def deal_redeem_type(value):
    if len(value) > 0:
        result = 0
        if value.find('网络') != -1 or value.find('微信') != -1:
            result += 1
        if value.find('电话') != -1:
            result += 2
        if value.find('手工') != -1:
            result += 4
        return result
    else:
        return ''


os.environ['TZ'] = 'Asia/Shanghai'

campaign_info = get_info('abc.xlsx')
print(campaign_info)

branch_info = get_branches('abc.xlsx', campaign_info['brand_name'])
if branch_info is None:
    print('fail')
else:
    print(branch_info)
# get_branches('abc.xls', '仙尚鲜')

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
