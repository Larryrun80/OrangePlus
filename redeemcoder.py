#!/usr/bin/env python
# filename:redeemcoder.py

import os
import math

import xlrd


def get_redeem_numbers(filename, sheet=0, column=0):

    """
    get redeem number from excel
    """

    if not os.path.exists(filename):
        return None

    data = xlrd.open_workbook(filename)
    table = data.sheets()[sheet]
    row_count = table.nrows
    col_count = table.ncols

    if column > col_count:
        return None

    redeem_numbers = []
    for i in range(row_count):
        redeem_numbers.append(table.cell(i, column).value)

    return redeem_numbers


def create_insert_lines(campaign_ids, redeem_codes):

    campaign_number = len(campaign_ids)
    redeem_code_number = len(redeem_codes)
    redeem_numbers_per_campaign = \
        math.floor(redeem_code_number / campaign_number)

    item_lines = []
    for ci in range(campaign_number):
        for i in range(redeem_numbers_per_campaign):
            line = "(" + str(campaign_ids[ci]) + ", '"
            line += redeem_codes[ci * redeem_numbers_per_campaign + i]
            line += "', 1, now(), now())"
            item_lines.append(line)

    return item_lines

cbs = (517112, 517113, 517114, 517115, 517116, 517117, 517118, 517119, 517120, 517121, 517122, 517123, 517124, 517125, 517126, 517127, 517128, 517129, 517130, 517131, 517132, 517133, 517134, 517135, 517136, 517137, 517138, 517139, 517140, 517141, 517142, 517143, 517144, 517145, 517146, 517147, 517148, 517149, 517150, 517151, 517152, 517153, 517154, 517155, 517156, 517157, 517158, 517159, 517160, 517161, 517162, 517163, 517164, 517165, 517166, 517167, 517168, 517169, 517170, 517171, 517172, 517173, 517174, 517175, 517176, 518320, 518321, 518322, 518323)
redeem_numbers = get_redeem_numbers('files/爱抢购鸡块和脆香鸡比萨.xlsx', 0, 1)
lines = create_insert_lines(cbs, redeem_numbers)
insert_sql = '''
    INSERT INTO redeem_number
    (campaign_branch_id, redeem_number, status, created_at, updated_at)
    VALUES
'''
for i in range(len(lines)):
    insert_sql += lines[i] + ', '
insert_sql = insert_sql[:-2] + ';'
print(insert_sql)
