# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/18 14:13
# @Author  : chao.li
# @File    : test_dtv_poweroff.py
# @Project : kpi_test
# @Software: PyCharm



import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - 码流使用 WhiteClipping.ts
    - dtv完成搜台
    - 进入通道

测试步骤
    - 息屏
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True, scope='module')
def setup_teardown(request):
    rdk_ir.wakeup()
    rdk_ir.enter_antenna()
    rdk_ir.send('enter')
    time.sleep(2)
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    time.sleep(1)
    yield
    rdk_ir.wakeup()
    rdk_ir.send('home')

@pytest.fixture(autouse=True)
def setup_teardown(request):
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_poweroff():
    rdk_ir.wakeup()
    rdk_ir.send('power')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, {'do':1,'ao':[800,1023]},sleep_time=0)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)