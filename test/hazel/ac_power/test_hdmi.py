# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/16 16:46
# @Author  : chao.li
# @File    : test_source.py
# @Project : kpi_test
# @Software: PyCharm

import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - 设置自启 Hdmi(手动)
    - 掉电
测试步骤
    - 上电
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(scope='module', autouse=True)
def teardown():
    yield
    hazel_ir.home()


@pytest.fixture(autouse=True)
def setup_teardown(request):
    # hazel_ir.default_input('Home')
    # hazel_ir.send('home')
    pytest.power_crt.switch(1, False)
    time.sleep(1)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_hdmi():
    pytest.power_crt.switch(1, True)
    pytest.kpi_result = pytest.kpi_result = pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[
        pytest.panel], time_out=180)
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)

