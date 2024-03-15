# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/26 13:33
# @Author  : chao.li
# @File    : test_wifi_connect.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - pin23 光敏贴在屏幕 x:50% y :47% 位置
    - 进入wifi连接界面
    - 光标移动到确认界面
测试步骤
    - 确认
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    # rdk_ir.home()


# @pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_wifi_scan():
    rdk_ir.send('enter')
    # kpi1 = pytest.light_sensor.count_kpi(1, {'do': 1, 'ao': [0, 350]}, sleep_time=0)
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, {'do': 0, 'ao': [0, 350]})
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
