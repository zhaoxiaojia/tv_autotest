# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 19:25
# @Author  : chao.li
# @File    : test_hdmi_goto_home.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - hdmi2通道接源
    - 源播放一张纯白图片
    - 进入通道 等待其完成
测试步骤
    - 回到home
    - 计算耗时
    
测试后置
    -
'''

@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.enter_input('HDMI2')
    rdk_ir.send('enter')
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    time.sleep(2)
@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_hdmi():
    rdk_ir.send('home')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, rdk_lux.get_note('launcher_50_40')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
