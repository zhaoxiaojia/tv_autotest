# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/19 11:28
# @Author  : chao.li
# @File    : test_home_goto_dtv.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - 推流WhiteClipping_4k.ts
    - 完成搜台 (手动)
    - 回到home

测试步骤
    - 进入dtv通道
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.send('home')


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv():
    kpi_1 = rdk_ir.enter_antenna()
    rdk_ir.send('enter')
    kpi_2 = pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    pytest.kpi_result = kpi_1 + kpi_2
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
