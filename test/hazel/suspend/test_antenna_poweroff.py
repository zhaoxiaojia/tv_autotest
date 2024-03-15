# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 14:26
# @Author  : chao.li
# @File    : test_atv_poweroff.py
# @Project : kpi_test
# @Software: PyCharm




import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - 使用54200 推送 纯白 pattern
    - tv完成搜台
    - 进入通道

测试步骤
    - 息屏
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.wakeup()
    hazel_ir.enter_input('Antenna')
    hazel_ir.send('enter')
    time.sleep(2)
    pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    time.sleep(1)
    yield
    hazel_ir.shutdown()
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    hazel_ir.send('home')

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_poweroff():
    hazel_ir.send('power')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, {'do':1,'ao':[800]},sleep_time=0)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)