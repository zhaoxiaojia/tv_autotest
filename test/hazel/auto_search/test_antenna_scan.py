# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 16:42
# @Author  : chao.li
# @File    : test_antenna_scan.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - 使用54200 推送 纯白 pattern

测试步骤
    - 搜台
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def set_default(request):
    hazel_ir.launcher_settings()
    pytest.executer.wait_and_tap('Live TV', 'text')
    pytest.executer.wait_element('Channel Scan', 'text')
    hazel_ir.send('up', wait_time=1)
    hazel_ir.send('enter', wait_time=1)
    yield
    hazel_ir.home()
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    time.sleep(2)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_search():
    pytest.executer.wait_element('Next', 'text')
    hazel_ir.send('enter')
    pytest.kpi_result = pytest.light_sensor.count_kpi(1, hazel_lux.get_note('pure_white_50_45')[pytest.panel], time_out=120,
                                              hold_times=10)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
