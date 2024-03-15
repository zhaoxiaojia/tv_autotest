# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/21 11:02
# @Author  : chao.li
# @File    : test_demo.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import time
from test.roku import *

import pytest

pattern_num = '033'
timing_num = '357'
# hative = '720'
# wative = '240'

test_pic = pytest.testResult.logDir + '/' + f'test_{pattern_num}.jpeg'
diff_pic = pytest.testResult.logDir + '/' + f'diff_{pattern_num}.jpeg'
target_pic = os.getcwd() + f'/tool/signal_generator/pattern/target_{pattern_num}.jpg'


@pytest.fixture(autouse=True, scope='session')
def setup_teardown():
	roku_ctl.switch_ir('off')
	pattern_gener.setTimmingPattern(timing_num, pattern_num)
	pattern_gener.switch_ctl('hdcp', 'off')
	roku_ctl["tvinput.hdmi1"].launch()
	pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')['Normal'])
	yield
	roku_ctl.switch_ir('on')
	# pattern_gener.close()
	roku_ctl.home()


@pytest.fixture(scope='module', params=['EcoSave', 'Vivid', 'Sports', 'Movie', 'Normal'])
def set_picture_mode(request):
	roku_ctl.set_picture_mode(request.param)


@pytest.fixture(scope='module', params=['Direct', 'Normal', 'Stretch', 'Zoom', 'Auto'])
def set_picture_size(request):
	roku_ctl.set_picture_size(request.param)


def test_hdmirx_info():
	roku_ctl.get_hdmirx_info()


# @pytest.mark.skip
def test_480i60_mode(set_picture_mode):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_mode}_{pattern_num}.jpeg'
	roku_ctl.capture_screen(test_pic)
	assert pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')[roku_ctl.ptc_mode]), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)


def test_480i60_size(set_picture_size):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_size_name}_{pattern_num}.jpeg'
	roku_ctl.capture_screen(test_pic)
	assert pytest.light_sensor.count_kpi(0, roku_lux.get_note(f'color_bar')['Normal']), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)
