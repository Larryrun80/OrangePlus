#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: createcampaign.py

import math
import os
import random
import re
import shutil
import string
import sys
import time

import xlrd
import requests
import pypinyin

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog


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

    # 初始化，从传入的参数动态创建属性
    def __init__(self, arg, db_handler, logger):
        if isinstance(arg, dict):
            self.set_attrs(arg)
            self.db_handler = db_handler
            self.logger = logger

    def set_attrs(self, dict_arg):
        for (item, item_type, required, col) in self.class_filter:
            # 如果在属性列表中，赋值
            if item in dict_arg.keys():
                if isinstance(dict_arg[item], item_type):
                    self.__dict__[col] = dict_arg[item]
                else:
                    raise RuntimeError(
                        'Invalid Type Detected with attrs %s' % item)
            # 如果是必需的属性而没在列表中
            elif required == 1:
                raise RuntimeError('Missing Info: %s' % item)

    # 检测是否已存在记录，用于避免插入数据冲突，如果需要避免重复，请重载
    def exists_recorder(self):
        return None

    # 将当前对象保存到对应的数据库中
    def persist(self):
        if '' == self.table_name:
            raise RuntimeError('Can Not Get Table Name')

        # 检测是否已存在记录
        recorders = self.exists_recorder()
        if recorders is not None:
            ids = ''
            for record in recorders:
                ids += str(record[0]) + ' '
            raise RuntimeError('%s EXISTS! id: %s' % (self.table_name, ids))

        # 构造列名和对应的值
        key_params = ''
        val_params = ''
        for key, val in self.__dict__.items():
            if 'db_handler' != key and 'logger' != key:
                key_params += '`' + key + '`, '
                if isinstance(val, str):
                    val_params += "'" + val + "', "
                else:
                    val_params += str(val) + ', '

        key_params = '({0})'.format(key_params[:-2])
        val_params = '({0})'.format(val_params[:-2])

        # 生成sql语句并执行
        sql = "INSERT INTO {table_name} {columns} VALUES {vals}".format(
            table_name=self.table_name, columns=key_params, vals=val_params)
        self.logger.info('='*10 + self.table_name + '='*10)
        self.logger.info(sql)

        cursor = self.db_handler.execute(sql)
        self.db_handler.commit()
        result = cursor.lastrowid
        return result


class Campaign(CampaignDealer):

    """docstring for Campaign"""

    class_filter = (
        ('brand_id', int, 1, 'brand_id'),
        ('item_id', int, 1, 'item_id'),
        ('start_time', str, 1, 'start_time'),
        ('end_time', str, 1, 'end_time'),
        ('market_price', float, 1, 'market_price'),
        ('stock', str, 1, 'stock'),
    )
    table_name = 'campaign'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def exists_recorder(self):
        # 需要判断在数据库中， item_id + brand_id 是唯一的
        sql = '''
        SELECT  id
        FROM    {table_name}
        WHERE   item_id = {item_id}
        AND     brand_id = {brand_id}
        '''.format(
            table_name=self.table_name,
            item_id=self.item_id,
            brand_id=self.brand_id)
        campaign = self.db_handler.execute(sql).fetchall()
        if len(campaign) == 0:
            return None
        else:
            return campaign

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        self.type = 1
        self.is_new = 1
        self.is_all_branch = 0
        self.floor_price = 1
        self.start_price = math.floor(self.market_price * 0.8)
        self.current_price = self.start_price
        self.unlock_price = self.start_price
        self.bargain_range = round((self.start_price-self.floor_price)/70, 1)
        self.redeem_period = 7
        return CampaignDealer.persist(self)


class CampaignBranch(CampaignDealer):

    """docstring for CampaignBranch"""

    class_filter = (
        ('campaign_id', int, 1, 'campaign_id'),
        ('start_time', str, 1, 'start_time'),
        ('end_time', str, 1, 'end_time'),
        ('market_price', float, 1, 'market_price'),
        ('stock', str, 1, 'stock'),
    )
    table_name = 'campaign_branch'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 0
        self.type = 1
        self.is_new = 1
        self.is_all_branch = 0
        self.floor_price = 1
        self.start_price = math.floor(self.market_price * 0.8)
        self.current_price = self.start_price
        self.unlock_price = self.start_price
        self.bargain_range = round((self.start_price-self.floor_price)/70, 1)
        self.redeem_period = 7
        self.left = self.stock
        self.freeze_period = 7
        self.online = 1
        self.weight = 0
        return CampaignDealer.persist(self)


class Brand(CampaignDealer):

    """docstring for Brand"""

    class_filter = (
        ('brand_name', str, 1, 'name'),
        ('company_name', str, 1, 'company_name'),
        ('brand_intro', str, 1, 'description'),
    )
    table_name = 'brand'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def exists_recorder(self):
        sql = '''
        SELECT  id, name
        FROM    {table_name}
        WHERE   name LIKE '%{brand_name}%'
        ;
        '''.format(table_name=self.table_name, brand_name=self.name)
        brand = self.db_handler.execute(sql).fetchall()
        if len(brand) == 0:
            return None
        else:
            return brand

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        return CampaignDealer.persist(self)


class Branch(CampaignDealer):

    """docstring for Branch"""

    class_filter = (
        ('brand_id', int, 1, 'brand_id'),
        ('city', int, 1, 'zone_id'),
        ('branch_name', str, 1, 'name'),
        ('brand_intro', str, 1, 'description'),
        ('redeem_type', int, 1, 'redeem_type'),
        ('address', str, 1, 'address'),
        ('phone', str, 0, 'tel'),
        ('work_hour', str, 0, 'redeem_time'),
        ('lat', float, 0, 'lat'),
        ('lng', float, 0, 'lng'),
    )
    table_name = 'branch'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        self.redeem_code_source = 1
        self.freeze_period = 7
        return CampaignDealer.persist(self)


class BranchContacter(CampaignDealer):

    """docstring for Branch_contacter"""

    class_filter = (
        ('branch_id', int, 0, 'branch_id'),
        ('phone', str, 1, 'tel'),
    )
    table_name = 'branch_contacter'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def exists_recorder(self):
        sql = '''
        SELECT  id
        FROM    {table_name}
        WHERE   tel = '{tel}'
        ;
        '''.format(table_name=self.table_name, tel=self.tel)
        bc = self.db_handler.execute(sql).fetchall()
        if len(bc) == 0:
            return None
        else:
            return bc

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        self.is_binding = 1
        return CampaignDealer.persist(self)


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

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.enabled = 1
        return CampaignDealer.persist(self)


class User(CampaignDealer):

    """docstring for User"""

    class_filter = (
        ('account', str, 1, 'username'),
    )
    table_name = 'user'

    def __init__(self, arg, db_handler, logger):
        CampaignDealer.__init__(self, arg, db_handler, logger)

    def exists_recorder(self):
        sql = '''
        SELECT  id
        FROM    {table_name}
        WHERE   username = '{username}'
        ;
        '''.format(table_name=self.table_name, username=self.username)
        user = self.db_handler.execute(sql).fetchall()
        if len(user) == 0:
            return None
        else:
            return user

    def persist(self):
        self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        self.password = time.strftime('%y%m%d')
        self.username_canonical = self.username
        self.email = self.username + '@branch.doweidu.com'
        self.email_canonical = self.email
        self.enabled = 1
        chars = string.ascii_lowercase + string.digits
        self.salt = ''.join([random.choice(chars) for i in range(31)])
        self.locked = 0
        self.expired = 0
        self.roles = 'a:0:{}'
        self.credentials_expired = 0
        return CampaignDealer.persist(self)


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
    # 第四个元素表示是否必须字段， True为必须，False不必须
    # 当前支撑的处理格式为: date, int, float
    # 遍历的时候为了节省资源，是在一次遍历中获取所有数据，获取到一个数据后在剩余cell查找下一个，所以需要保证content中的顺序符合先左后右先上后下的原则
    brand_contents = (
        ('brand_name', '商户名称（线上展示）', '', True),
        ('company_name', '公司名称（合同签约方）', '', True),
        ('city', '所在城市', 'int', True),
        ('brand_intro', '公司或品牌简介', '', True),
        ('email', '商户邮箱', '', False)
    )

    item_contents = (
        ('item_name', '商品名称', '', True),
        ('market_price', '市场价格', 'float', True),
        ('stock', '每日供应量', '', True),
        ('start_time', '上线日期', 'date', True),
        ('end_time', '下线日期', 'date', True),
        ('item_intro', '商品详细描述（特色/成分/口感/功效等）', '', True),
    )

    result = {}     # 存储返回结果
    brand = {}      # 存储解析到的品牌信息
    item = {}       # 存储解析到的单个商品信息
    items = []      # 存储解析到的所有商品信息

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

    # 检测是否文件格式被更改（brand 部分）
    is_file_correct = True
    brand_keys = []
    for b_item in brand_contents:
        if b_item[3]:
            brand_keys.append(b_item[0])

    for key in brand_keys:
        if key not in brand.keys():
            is_file_correct = False
            missing_key = key
            break

    if not is_file_correct:
        raise RuntimeError('Reading Data Failed, Not Include %s' % missing_key)
    # 将city转化为id
    tmp_city = get_city_id(brand['city'])
    if tmp_city == 0:
        raise RuntimeError('City Not Found: %s' % brand['city'])
    else:
        brand['city'] = tmp_city

    # 创建brand账号
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
                    value += ' 02:00:00'
                # 对价格部分， 从字符串中提取整数或浮点数
                if(item_contents[key_index][2] == 'float'):
                    value = float(re.findall('\d*\.\d+|\d+', value)[0])
                item[item_contents[key_index][0]] = value
                if key_index < len(item_contents) - 1:
                    key_index = key_index + 1
                # 如果一个商品处理完了，新建一个商品
                elif key_index == len(item_contents) - 1:
                    key_index = 0
                    items.append(item)
                    item = {}

    if 0 == len(items):
        raise RuntimeError('Reading Data Failed, Incorrect Item Info')

    result['items'] = items
    return result


def find_content(origin_string, key_name):
    '''
        从一个cell中过滤掉提示文字，获得需要的内容
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


def get_city_id(city_name):
    '''
        将城市名转化为城市id
    '''
    cities = {
        '北京': 10,
        '上海': 21,
        '杭州': 571,
        '深圳': 755,
        '沈阳': 2101,
        '大连': 2102,
        '大庆': 2306,
        '南京': 3201,
        '苏州': 3205,
        '济南': 3701,
        '武汉': 4201,
        '广州': 4401,
    }

    city_id = 0
    for city in cities.keys():
        if city_name.find(city) > -1:
            city_id = cities[city]
            break
    return city_id


def generate_account(brand_name, pattern=0):
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')

    chinese_name = ''
    for i in range(len(brand_name)):
        if zhPattern.search(brand_name[i]):
            chinese_name += brand_name[i]

    if '' == chinese_name:
        raise RuntimeError('No Chinese Character Found: %s', brand_name)

    brand_account = ''
    if 0 == pattern:
        # pattern 0 的生成规则为拼音首字母
        for j in range(len(chinese_name)):
            brand_account += pypinyin.pinyin(
                chinese_name[j], pypinyin.FIRST_LETTER)[0][0]
    if is_username_exists(brand_account, db_handler):
        raise RuntimeError('Brand User Name Exist: %s', brand_account)
    else:
        return brand_account


def get_branch_account(prefix, db_handler, index=0):
    is_username_not_available = True
    username = ''
    while is_username_not_available:
        index += 1
        username = prefix + str(index)
        is_username_not_available = is_username_exists(username, db_handler)
    return username


def is_username_exists(username, db_handler):
    sql = '''
        SELECT  id
        FROM    user
        WHERE   username = '{username}'
        ;
    '''.format(username=username)
    user = db_handler.execute(sql).fetchall()
    return len(user) > 0


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

    if col_count < len(branch_format):
        raise RuntimeError('Branch Info Error')

    # branch_row定义了从哪一行开始门店数据
    branch_row = 0
    for i in range(row_count):
        cell_value = str(table.cell(i, 0).value).strip()
        if '分店名称' in cell_value:
            branch_row = i + 1
            break

    branches = []  # 用于存储处理好的门店
    # 如果某一行最后一列的值为空，代表着这行不是门店信息了
    while table.cell(branch_row, col_count-1).value != '':
        branch = {}
        # 遍历存储某个门店的全部信息
        for i in range(len(branch_format)):
            branch[branch_format[i]] = str(table.cell(branch_row, i).value).strip()
        if '' == branch['brand_name'] or '' == branch['address']:
            raise RuntimeError('Branch Name Or Address Missing')

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
        branch_row = branch_row + 1
    return branches


def get_lat_lng_using_address(address, city=None):
    '''
        通过地址文字获取坐标
        调用soso地图API
        如果获取失败，返回(0, 0)
    '''

    request_url = 'http://apis.map.qq.com/ws/geocoder/v1'
    key = '3OUBZ-QW53G-Q5DQ4-I6RTL-UFK53-POFWA'  # soso的开发者key
    request_url += '?address=' + address + '&key=' + key
    if city is not None:
        request_url += '&region=' + city

    try:
        response = requests.get(request_url, timeout=(5, 50)).json()
        if response['status'] != 0:
            return (0.0, 0.0)
        elif response['result']['deviation'] == -1:
            return (0.0, 0.0)
        else:
            return (response['result']['location']['lng'],
                    response['result']['location']['lat'],)
    except:
        return (0.0, 0.0)


def deal_phone_number(value):
    # 如果是float类型， 取整
    if isinstance(value, float):
        value = str(int(value))
    # 如果是string类型， 取数字
    if isinstance(value, str):
        value = ''.join([i for i in value if i.isdigit()])

    # 如果不是手机号，且不是0开头， 加0
    if len(value) > 0 and (
        len(value) != 11 or (
            len(value) == 11 and value[0] != '1')) and value[0] != '0':
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
        raise RuntimeError('No Redeem Type Found')


def create_relation(arg, db_handler, logger):
    '''
        建立关联表
        arg传入一个dict，格式为：
        {
            'table_name': table_name,
            'columns': (('column_name', 'value'), ('column_name', 'value'))
        }
    '''
    if isinstance(arg, dict) and len(arg.keys()) == 2\
            and 'table_name' in arg.keys() and 'columns' in arg.keys():
        try:
            sql = 'INSERT INTO  {table_name} ({col1}, {col2}) VALUES ({value1}, {value2});'.format(table_name=arg['table_name'], col1=arg['columns'][0][0], col2=arg['columns'][1][0], value1=arg['columns'][0][1], value2=arg['columns'][1][1])
            logger.info(sql)
            db_handler.execute(sql)
            db_handler.commit()
        except RuntimeError as e:
            logger.info(e)
    else:
        raise RuntimeError('Create Relation Failed: Pls Check Param')


def deal_file(file_name, redeem_limited=True):
    try:
        campaign_info = get_info(file_name)
        if campaign_info is not None:
            branch_info = get_branches(file_name)
            logger.info('*'*20 + campaign_info['brand']['brand_name'] + '*'*20)
            print('*'*20 + campaign_info['brand']['brand_name'] + '*'*20)

            if branch_info is not None:
                brand = Brand(campaign_info['brand'], db_handler, logger)
                brand_id = brand.persist()
                brand_user = User(campaign_info['brand'], db_handler, logger)
                brand_user_id = brand_user.persist()
                # 关联brand user
                brand_arg = {
                    'table_name': 'brand_users',
                    'columns': (
                        ('brand_id', brand_id),
                        ('user_id', brand_user_id),
                    )
                }
                create_relation(brand_arg, db_handler, logger)

                # 开始处理 branch 相关信息
                branches = []
                branch_index = 0
                for branch_item in branch_info:
                    branch_item['brand_id'] = int(brand_id)
                    branch_item['city'] = campaign_info['brand']['city']
                    branch_item['brand_intro'] = campaign_info['brand']['brand_intro']
                    branch_item['account'] = get_branch_account(
                        campaign_info['brand']['account'], db_handler, branch_index)
                    branch = Branch(branch_item, db_handler, logger)
                    branch_id = branch.persist()
                    branch_item['branch_id'] = branch_id
                    branches.append(branch_id)
                    branch_index += 1

                    # 处理 branch_contacter
                    if branch_item['redeem_type'] in (2, 3, 7):
                        branch_contacter = BranchContacter(
                            branch_item, db_handler, logger)
                        branch_contacter.persist()

                    # 处理 branch_user
                    branch_user = User(branch_item, db_handler, logger)
                    branch_user_id = branch_user.persist()
                    # 关联branch user
                    branch_arg = {
                        'table_name': 'branch_users',
                        'columns': (
                            ('branch_id', branch_id),
                            ('user_id', branch_user_id),
                        )
                    }
                    create_relation(branch_arg, db_handler, logger)

                # 开始处理item和campaign branch
                for info_item in campaign_info['items']:
                    # 处理item
                    info_item['brand_id'] = int(brand_id)
                    info_item['brand_intro'] = campaign_info['brand']['brand_intro']
                    item = Item(info_item, db_handler, logger)
                    item_id = item.persist()
                    info_item['item_id'] = item_id

                    # 处理campaign
                    campaign = Campaign(info_item, db_handler, logger)
                    campaign_id = campaign.persist()
                    info_item['campaign_id'] = campaign_id

                    # 处理campaign branch
                    campaign_branches = []

                    if redeem_limited:
                        # cb_count为生成的campaign branch数量
                        cb_count = len(branches)
                    else:
                        cb_count = 1
                    for i in range(cb_count):
                        campaign_branch = CampaignBranch(info_item, db_handler, logger)
                        campaignbranch_id = campaign_branch.persist()
                        campaign_branches.append(campaignbranch_id)

                    # 关联campaignbranch 和 branch
                    if cb_count == 1:  # 单店或通兑
                        for branch_id in branches:
                            cbb_arg = {
                                'table_name': 'campaignbranch_has_branches',
                                'columns': (
                                    ('campaignbranch_id', campaignbranch_id),
                                    ('branch_id', branch_id),
                                )
                            }
                            create_relation(cbb_arg, db_handler, logger)
                    else:       # 多店非通兑
                        for i in range(cb_count):
                            cbb_arg = {
                                'table_name': 'campaignbranch_has_branches',
                                'columns': (
                                    ('campaignbranch_id', campaign_branches[i]),
                                    ('branch_id', branches[i]),
                                )
                            }
                            create_relation(cbb_arg, db_handler, logger)
        print('done')
    except RuntimeError as e:
        print(e)
        logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))

########################## START WORK ##################################

os.environ['TZ'] = 'Asia/Shanghai'
db_handler = OrangeMySQL('DB_ORANGE')
logger = OrangeLog('LOG_ORANGE', 'CREATER').getLogger()

base_dir = os.path.split(os.path.realpath(__file__))[0] + '/files/creater'
limit_dir = base_dir + '/limited'           # 非通兑源文件路径
if not os.path.exists(limit_dir):
    os.makedirs(limit_dir)
no_limit_dir = base_dir + '/notlimited'     # 通兑源文件路径
if not os.path.exists(no_limit_dir):
    os.makedirs(no_limit_dir)
dealed_dir = base_dir + '/dealed'           # 处理后文件路径
if not os.path.exists(dealed_dir):
    os.makedirs(dealed_dir)

redeem_limited = True  # true表示非通兑，false为通兑

# 处理非通兑商品
for filename in os.listdir(limit_dir):
    if filename[0] != '.':
        print('Dealing {0}'.format(filename))
        origin_filename = limit_dir + '/' + filename
        dealed_filename = dealed_dir + '/l_' + filename
        deal_file(origin_filename, True)
        shutil.move(origin_filename, dealed_filename)

# 处理通兑商品
for filename in os.listdir(no_limit_dir):
    if filename[0] != '.':
        print('Dealing {0}'.format(filename))
        origin_filename = no_limit_dir + '/' + filename
        dealed_filename = dealed_dir + '/nl_' + filename
        deal_file(origin_filename, False)
        shutil.move(origin_filename, dealed_filename)

db_handler.close()

