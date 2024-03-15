# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 16:26
# @Author  : chao.li
# @File    : test_composite_goto_antenna.py
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
    - 进入Composite
    
测试步骤
    - 切换
    - 计算耗时

测试后置
    -
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    hazel_ir.enter_input('Composite')
    hazel_ir.send('enter')
    pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    yield
    hazel_ir.home()
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    time.sleep(2)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_composite():
    hazel_ir.switch_input('Antenna')
    hazel_ir.send('enter')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, hazel_lux.get_note('launcher_50_40')[pytest.panel],inflection_point=[[750,950]])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
