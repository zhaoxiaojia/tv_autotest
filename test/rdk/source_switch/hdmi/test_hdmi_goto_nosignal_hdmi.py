# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/18 19:06
# @Author  : chao.li
# @File    : test_hdmi_goto_nosignal_hdmi.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - pin23 光敏贴在屏幕 x:90% y :10% 位置
    - hdmi2播放pure_white_4k.png 并进入
    - hdmi1不接源 
测试步骤
    - 切换到hdmi1
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.home()
    rdk_ir.enter_input('HDMI2')
    rdk_ir.send('enter')
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel], inflection_point=[[750, 950]])
    time.sleep(3)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.home()


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_hdmi():
    rdk_ir.enter_input('HDMI3')
    rdk_ir.send('enter')
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, rdk_lux.get_note('pure_white_50_45')[pytest.panel],
                                              inflection_point=[[750, 950]])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
