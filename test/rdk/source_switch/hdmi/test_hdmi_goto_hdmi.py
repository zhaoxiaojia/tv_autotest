# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/18 17:06
# @Author  : chao.li
# @File    : test_hdmi_goto_hdmi.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - hdmi2播放pure_white_4k.png
    - hdmi3播放pure_white_4k.png
    - 进入hdmi2 
测试步骤
    - 切换到hdmi3
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.home()
    rdk_ir.enter_input('HDMI2')
    rdk_ir.send('enter')
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    time.sleep(3)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.home()

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_hdmi():
    rdk_ir.enter_input('HDMI1')
    rdk_ir.send('enter')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel], inflection_point=[[750,950]])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
