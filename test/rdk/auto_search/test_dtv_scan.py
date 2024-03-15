# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 11:06
# @Author  : chao.li
# @File    : test_dtv_scan.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置:
    - pin23 传感器 贴在屏幕 x:40% y:40% 位置
    - 进入antenna 通道

测试步骤:
    - 点击搜台
    - 搜台完成
    - 计算耗时
    
测试后置:
    - 回到home

'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.antenna_scan()
    time.sleep(1)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.send('home')


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv_scan():
    rdk_ir.send('enter')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel], inflection_point=[[500, 700]],
                                time_out=120)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
