# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/26 10:05
# @Author  : chao.li
# @File    : test_wifi_scan.py
# @Project : kpi_test
# @Software: PyCharm




import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - pin23 光敏贴在屏幕 x:90% y :80% 位置
    - 进入network 设置
测试步骤
    - wifi scan
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.enter_settings('Network')
    rdk_ir.send('enter')
    time.sleep(2)
    for _ in range(2):
        rdk_ir.send('down')
        time.sleep(0.5)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.home()

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_wifi_scan():
    rdk_ir.send('down')
    pytest.kpi_result =pytest.light_sensor.count_kpi(1, rdk_lux.get_note('wifi_scan')[pytest.panel],sleep_time=0.1)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
