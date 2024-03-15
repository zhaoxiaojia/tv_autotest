# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/19 14:18
# @Author  : chao.li
# @File    : test_hdmi_goto_dtv.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.rdk import *

import pytest

'''
测试前置
    - hdmi播放pure_white_4k.png 并进入
    - 推流播放WhiteClipping_4k.ts
    - 完成搜台(手动)
测试步骤
    - 切换到dtv
    - 计算耗时

测试后置
    - 回到home
'''


@pytest.fixture(autouse=True)
def setup_teardown(request):
    rdk_ir.home()
    rdk_ir.enter_input('HDMI2')
    rdk_ir.send('enter')
    pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel])
    time.sleep(3)
    yield
    pytest.result_data[request.module.__name__].append(pytest.kpi_result)
    rdk_ir.home()


@pytest.mark.repeat(pytest.repeat_count)
@pytest.mark.half_auto
def test_hdmi():
    kpi_1 = rdk_ir.enter_antenna()
    rdk_ir.send('enter')
    kpi_2 = pytest.light_sensor.count_kpi(0, rdk_lux.get_note('pure_white_50_45')[pytest.panel],
                                         inflection_point=[[750, 950]])
    pytest.kpi_result = kpi_1 + kpi_2
    logging.info(f'kpi {kpi_1 + kpi_2} secnods')
    time.sleep(1)
