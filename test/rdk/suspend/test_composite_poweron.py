# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/16 13:30
# @Author  : chao.li
# @File    : test_composite_poweron.py
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
    - 设置开启 自启Composite
    - 息屏

测试步骤
    - 点亮
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True, scope='module')
def set_default():
    rdk_ir.wakeup()
    rdk_ir.default_input('Composite')
    rdk_ir.send('home')
    yield
    rdk_ir.default_input('Home')
    rdk_ir.send('home')


@pytest.fixture(autouse=True)
def setup_teardown(request):
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_poweron():
    rdk_ir.shutdown()
    rdk_ir.send('power')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)