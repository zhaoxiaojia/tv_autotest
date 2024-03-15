# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 15:21
# @Author  : chao.li
# @File    : test_home_goto_youtube.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - pin23传感器 贴在屏幕 x:85% y:90% 位置
    - 确保平台连接外网

测试步骤
    - 点击进入youtube
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.home()
    rdk_serial.kill_app('cobalt')
    time.sleep(1)
    rdk_ir.app('youtube')
    time.sleep(1)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.send('home')


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv_scan():
    rdk_ir.send('enter')
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, rdk_lux.get_note('youtube_85_90')[pytest.panel],
                                              inflection_point=[[800, 1000]], time_out=60)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
