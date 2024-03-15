# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/16 14:34
# @Author  : chao.li
# @File    : test_home_goto_netflix.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - pin23传感器 贴在屏幕 x:15% y:70% 位置
    - 确保平台连接外网

测试步骤
    - 点击进入Netflix
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.home()
    pytest.executer.app_stop('com.netflix.ninja')
    time.sleep(1)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    hazel_ir.send('home')


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv_scan():
    hazel_ir.send('netflix')
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, hazel_lux.get_note('netflix_15_70')[pytest.panel], hold_times=10,
                                              inflection_point=[[800, 1023]], time_out=120)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(5)
