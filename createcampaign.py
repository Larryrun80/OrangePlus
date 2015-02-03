#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: createcampaign.py

import re
import time
import os
import sys

import xlrd
import requests
import pypinyin

from orangejuice.utils.orangemysql import OrangeMySQL


class CampaignDealer:

    '''
        处理所有类数据的基类
    '''

    # 这个类中的属性，每个属性用一个元组表示
    # 第一个元素是输入内容的key
    # 第二个元素是属性类型，这个属性类型必需是isinstance可以识别的
    # 第三个元素表示这个属性是否必需，必需为1，否则为0
    # 第四个元素是数据库的列名，属性名也使用这个字段
    # filter应该被每个继承类覆盖
    class_filter = (
        ('item1_name', str, 1, 'column1_name'),
        ('item2_name', int, 0, 'column2_name'),
    )

    # 数据表名，必需被重载
    table_name = ''

    def __init__(self, arg, db_handler):
        if isinstance(arg, dict):
            self.set_attrs(arg)
            self.db_handler = db_handler

    def set_attrs(self, dict_arg):
        for (item, item_type, required, col) in self.class_filter:
            # 如果在属性列表中，赋值
            if item in dict_arg.keys():
                if isinstance(dict_arg[item], item_type):
                    self.__dict__[col] = dict_arg[item]
                else:
                    raise RuntimeError('Invalid Type Detected with attrs %s', item)
            # 如果是必需的属性而没在列表中
            elif required == 1:
                raise RuntimeError('Missing Info: %s', item)

    def exists_recorder(self):
        return None

    def persist(self):
        if '' == self.table_name:
            raise RuntimeError('Can Not Get Table Name')

        if self.exists_recorder() is not None:
            raise RuntimeError('EXISTS!')

        key_params = ''
        val_params = ''
        for key, val in self.__dict__.items():
            if 'db_handler' != key:
                key_params += key + ', '
                if isinstance(val, str):
                    val_params += "'" + val + "', "
                else:
                    val_params += str(val) + ', '

        key_params = '({0})'.format(key_params[:-2])
        val_params = '({0})'.format(val_params[:-2])

        sql = "INSERT INTO {table_name} {columns} VALUES {vals}".format(table_name=self.table_name, columns=key_params, vals=val_params)

        cursor = self.db_handler.execute(sql)
        self.db_handler.commit()
        result = cursor.lastrowid
        return result


class Campaign(CampaignDealer):

    """docstring for Campaign"""

    def __init__(self, arg):
        super(Campaign, self).__init__()
        self.arg = arg


class CampaignBranch(CampaignDealer):

    """docstring for CampaignBranch"""

    def __init__(self, arg):
        super(CampaignBranch, self).__init__()
        self.arg = arg


class Brand(CampaignDealer):

    """docstring for Brand"""

    class_filter = (
        ('brand_name', str, 1, 'name'),
        ('company_name', str, 1, 'company_name'),
        ('brand_intro', str, 1, 'description'),
    )
    table_name = 'brand'

    def __init__(self, arg, db_handler):
        CampaignDealer.__init__(self, arg, db_handler)

    def exists_recorder(self):
        sql = '''
        SELECT  id, name
        FROM    {table_name}
        WHERE   name LIKE '{brand_name}%'
        '''.format(table_name=self.table_name, brand_name=self.name)
        brand = self.db_handler.execute(sql).fetchall()
        if len(brand) == 0:
            return None
        else:
            return brand

    def persist(self, db_handler):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        return CampaignDealer.persist(self)

class Branch(CampaignDealer):

    """docstring for Branch"""

    def __init__(self, arg):
        super(Branch, self).__init__()
        self.arg = arg


class Item(CampaignDealer):

    """docstring for Item"""

    class_filter = (
        ('brand_id', int, 1, 'brand_id'),
        ('item_name', str, 1, 'name'),
        ('item_intro', str, 0, 'description'),
        ('brand_intro', str, 0, 'more_info'),
        ('market_price', float, 0, 'market_price'),
    )
    table_name = 'item'

    def __init__(self, arg, db_handler):
        CampaignDealer.__init__(self, arg, db_handler)

    def persist(self, db_handler):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        return CampaignDealer.persist(self)


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
    if not os.path.exists(file_name):
        return None

    data = xlrd.open_workbook(file_name)
    table = data.sheets()[0]
    row_count = table.nrows
    col_count = table.ncols

    # 定义所有需要的数据，用元组表示每一组数据
    # 第一个元素是用来存储数据的key，第二个是excel中的数据指示（需写全）
    # 第三个元素是需要处理为什么格式，''表示不需处理
    # 当前支撑的处理格式为: date, int, float
    # 遍历的时候为了节省资源，是在一次遍历中获取所有数据，获取到一个数据后在剩余cell查找下一个，所以需要保证content中的顺序符合先左后右先上后下的原则
    brand_contents = (
        ('brand_name', '商户名称（线上展示）', ''),
        ('company_name', '公司名称（合同签约方）', ''),
        ('city', '所在城市', ''),
        ('brand_intro', '公司或品牌简介', ''),
    )

    item_contents = (
        ('item_name', '商品名称', ''),
        ('market_price', '市场价格', 'float'),
        ('stock', '每日供应量', ''),
        ('start_time', '上线日期', 'date'),
        ('end_time', '下线日期', 'date'),
        ('item_intro', '商品详细描述（特色/成分/口感/功效等）', ''),
    )

    result = {}
    brand = {}
    item = {}
    items = []
    # key_index 是内容下标，读取到一个值后移动到下一个需要读取的值
    key_index = 0

    # 获取brand信息
    for i in range(row_count):
        for j in range(col_count):
            cell_value = str(table.cell(i, j).value).strip()
            # 如果含有对应的指示文字
            if brand_contents[key_index][1] in cell_value:
                value = find_content(cell_value, brand_contents[key_index][1])
                brand[brand_contents[key_index][0]] = value
                if key_index < len(brand_contents) - 1:
                    key_index = key_index + 1

    brand['account'] = generate_account(brand['brand_name'])
    result['brand'] = brand

    key_index = 0
    # 获取商品信息
    for i in range(row_count):
        for j in range(col_count):
            cell_value = str(table.cell(i, j).value).strip()
            # 如果含有对应的指示文字
            if item_contents[key_index][1] in cell_value:
                value = find_content(cell_value, item_contents[key_index][1])
                # 对日期类型，提取所有数字并加上-， 形成yyyy-mm-dd格式
                if(item_contents[key_index][2] == 'date'):
                    value = '-'.join(re.findall('\d+', value))
                # 对价格部分， 从字符串中提取整数或浮点数
                if(item_contents[key_index][2] == 'float'):
                    value = float(re.findall('\d*\.\d+|\d+', value)[0])
                item[item_contents[key_index][0]] = value
                if key_index < len(item_contents) - 1:
                    key_index = key_index + 1
                elif key_index == len(item_contents) - 1:
                    key_index = 0
                    items.append(item)
                    item = {}

    result['items'] = items
    return result


def generate_account(brand_name, level=0):
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    if brand_name is None or not zhPattern.search(brand_name):
        raise RuntimeError('No Chinese Character Found: %s', brand_name)

    brand_account = ''
    if 0 == level:
        # level 0 的生成规则为拼音首字母
        for j in range(len(brand_name)):
            brand_account += pypinyin.pinyin(brand_name[j], pypinyin.FIRST_LETTER)[0][0]
        return brand_account


def get_branches(file_name, city=None):

    '''
        从excel获取所有门店信息
    '''

    if not os.path.exists(file_name):
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
        if value.find('手工') != -1 or value.find('纸质') != -1:
            result += 4
        return result
    else:
        return 0


os.environ['TZ'] = 'Asia/Shanghai'
db_handler = OrangeMySQL('DB_ORANGE')
file_name = 'abc.xls'

try:
    campaign_info = get_info(file_name)
    if campaign_info is not None:
        branch_info = get_branches(file_name)
        print(campaign_info)
        print(branch_info)

        if branch_info is not None:
            brand = Brand(campaign_info['brand'], db_handler)
            brand_id = brand.persist(db_handler)

            for info_item in campaign_info['items']:
                info_item['brand_id'] = int(brand_id)
                info_item['brand_intro'] = campaign_info['brand']['brand_intro']
                item = Item(info_item, db_handler)
                item_id = item.persist(db_handler)

    db_handler.close()
except RuntimeError as e:
    print(e)
