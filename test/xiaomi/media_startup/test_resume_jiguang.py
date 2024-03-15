# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 10:18
# @Author  : chao.li
# @File    : test_resume_jiguang.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.xiaomi import *

import pytest

'''
测试前置
    - 安装云视听极光

测试步骤
    - 点击进入极光
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    xiaomi_adb.yunshiting_jiguang()
    time.sleep(1)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    # xiaomi_ir.send('home')


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv_scan():
    pytest.executer.enter()
    logging.info(xiaomi_lux.get_note('yunshiting_jiguang')[pytest.panel])
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, xiaomi_lux.get_note('yunshiting_jiguang')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(5)
