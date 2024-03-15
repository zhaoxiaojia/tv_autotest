# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/13 10:20
# @Author  : chao.li
# @File    : test_home_poweron.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - 回到home
    - 确保 dut 为息屏状态
   
测试步骤
    - 唤醒
    - 计算耗时
    
测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.shutdown()
    yield
    rdk_ir.wakeup()
    rdk_ir.send('home')
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    time.sleep(2)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_poweron():
    rdk_ir.send('power')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, rdk_lux.get_note('launcher_50_40')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
