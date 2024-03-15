# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/12 11:08
# @Author  : chao.li
# @File    : test_home_power.py
# @Project : kpi_test
# @Software: PyCharm



import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - 回到home
    - 确保dut为亮屏状态

测试步骤
    - 息屏
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.wakeup()
    hazel_ir.home()
    yield
    hazel_ir.wakeup()
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    hazel_ir.send('home')

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_poweroff():
    hazel_ir.send('power')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, {'do':1,'ao':[800]},sleep_time=0)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)