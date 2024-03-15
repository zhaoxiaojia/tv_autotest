# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 15:34
# @Author  : chao.li
# @File    : test_home_goto_antenna.py
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
    - 回到home

测试步骤
    - 进入Composite通道
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.home()
    hazel_ir.enter_input('Antenna')
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    hazel_ir.send('home')

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_atv():
    hazel_ir.send('enter')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
