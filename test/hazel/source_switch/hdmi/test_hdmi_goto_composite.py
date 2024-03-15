# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/12 17:20
# @Author  : chao.li
# @File    : test_hdmi_goto_composite.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - hdmi播放pure_white_4k.png 并进入
    - composite播放pure_white_4k.png
    
测试步骤
    - 切换到composite
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.home()
    hazel_ir.enter_input('HDMI1')
    hazel_ir.send('enter')
    pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    time.sleep(3)
    yield
    hazel_ir.home()
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    hazel_ir.home()


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_hdmi():
    hazel_ir.switch_input('Composite')
    hazel_ir.send('enter')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel],
                                              inflection_point=[[750, 950]])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
