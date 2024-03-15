# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/12 15:10
# @Author  : chao.li
# @File    : test_hdmi_poweron.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - Hdmi1通道接源
    - 源需要播放一张纯白图片
    - 设置开启 自启hdmi
    - 息屏

测试步骤
    - 点亮
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(scope='module', autouse=True)
def set_default():
    hazel_ir.wakeup()
    hazel_ir.default_input('Last Input')
    hazel_ir.send('home')
    hazel_ir.enter_input('HDMI1')
    hazel_ir.send('enter')
    pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    yield
    hazel_ir.wakeup()
    hazel_ir.default_input('Home')
    hazel_ir.send('home')


@pytest.fixture(autouse=True)
def setup_teardown(request):
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.full_auto
def test_poweron():
    hazel_ir.shutdown()
    hazel_ir.send('power')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, hazel_lux.get_note('pure_white_50_45')[pytest.panel])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    time.sleep(1)
