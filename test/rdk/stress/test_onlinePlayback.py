# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/3 19:16
# @Author  : chao.li
# @File    : test_onlinePlayback.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - 确保平台连接外网

测试步骤
    - 点击进入Netflix并播放
    - 点击进入Youtube并播放

测试后置
    - 回到home
'''


# @pytest.fixture(autouse=True)
# def setup_teardown(request):
#     yield
#     pytest.result_data[request.module.__name__].append(pytest.kpi_result)
#     rdk_ir.send('home')


def test_online():
    while True:
        # 播放 netflix
        rdk_ir.app('netflix')
        time.sleep(10)
        rdk_ir.send('enter')
        time.sleep(5)
        rdk_ir.send('enter')
        time.sleep(20)
        rdk_ir.send('home')
        time.sleep(20)
        # 播放 youtube
        rdk_ir.app('youtube')
        time.sleep(10)
        rdk_ir.send('enter')
        time.sleep(5)
        rdk_ir.send('enter')
        time.sleep(20)
        rdk_ir.send('home')
        time.sleep(20)
