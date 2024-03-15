# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/16 15:46
# @Author  : chao.li
# @File    : test_home_goto_composite.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - Composite通道接源
    - 源需要播放一张纯白图片
    - 回到home

测试步骤
    - 进入Composite通道
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.send('home')
    time.sleep(2)
    rdk_ir.enter_input('Composite')
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.send('home')

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_composite():
    rdk_ir.send('enter')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
