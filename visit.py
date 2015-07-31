#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: visit.py

import random

import requests


def visit_url(url):
    ip = gen_random_ip()
    headers = {'X-Forwarded-For': ip, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Cookie': 'BAIDUID=CB4E23DECA1A957AFBE9B488F14220C7:FG=1; HMACCOUNT=B7AC5C97D92BDA6D; BDUSS=Vd2SWQwQ0JqTmxFQUZXNzEtZXBXMUx-bS1kQXp4SUdpclVaZlhnS2gzSnBzRTVWQVFBQUFBJCQAAAAAAAAAAAEAAAD3jBlVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGkjJ1VpIydVL; BIDUPSID=CB4E23DECA1A957AFBE9B488F14220C7; SFSSID=ujqmdkd04kq6plhrvbupb6i5l7; uc_login_unique=826a9fce80f657a6a27d64eb5b2af8d9; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a01812002266; BDRCVFR[avTmVgHiSfR]=mk3SLVN4HKm; H_PS_PSSID=13669_13783_1445_13843_13075_12824_12868_13322_13691_10562_12722_13892_13210_13762_13257_13780_12360_13838_13505_13086_8498; HMVT=09c5d4daddb9b6250ba93075257e58a2|1431189476|', 'Host': 'hm.baidu.com', 'Referer': 'http://html5.iqianggou.com/app/test'}
    r = requests.get(url, headers=headers)
    print(r.request.headers)


def gen_random_ip():
    ip = str(random.randint(1, 254)) + '.'\
            + str(random.randint(1, 254)) + '.'\
            + str(random.randint(1, 254)) + '.'\
            + str(random.randint(1, 254))
    print(ip)
    return ip

#VISIT_BASE_URL = 'http://html5.iqianggou.com'
VISIT_BASE_URL = 'http://hm.baidu.com/hm.js?0b605b6a800f5f0d308f3517d7b55a39'

for i in range(10):
    visit_url(VISIT_BASE_URL)
