# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/16 13:53
# @Author  : chao.li
# @File    : test_antenna_switch_channel.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.hazel import *

import pytest

'''
测试前置
    - 推流播放US-MN(DTV2.1)Multi-language.ts
    - 完成搜台(手动)
    - 进入antenna

测试步骤
    - 切换到hdmi
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True, scope='module')
def setup_teardown(request):
    hazel_ir.enter_input('Antenna')
    hazel_ir.send('enter')
    pytest.light_sensor.count_kpi(0, {'do': 2, 'ao': [0, 750]}, inflection_point=[[750, 830]])
    yield
    hazel_ir.home()


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_dtv(request):
    hazel_ir.send('channel_down')
    pytest.kpi_result = pytest.light_sensor.count_kpi(0, {'do': 2, 'ao': [0, 750]}, inflection_point=[[750, 830]])
    logging.info(f'kpi {pytest.kpi_result} secnods')
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    time.sleep(1)
