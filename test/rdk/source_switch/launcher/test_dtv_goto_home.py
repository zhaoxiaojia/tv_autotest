# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/19 13:34
# @Author  : chao.li
# @File    : test_dtv_goto_home.py
# @Project : kpi_test
# @Software: PyCharm



import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - 推流WhiteClipping_4k.ts
    - 完成搜台 (手动)
    - 进入dtv通道

测试步骤
    - 回到home
    - 计算耗时

测试后置
    - 
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.enter_antenna()
    rdk_ir.send('enter')
    time.sleep(5)
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.send('home')
    time.sleep(2)

@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv():
    rdk_ir.send('home')
    pytest.kpi_result =pytest.light_sensor.count_kpi(0, rdk_lux.get_note('launcher_50_40')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
