# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_C84498.py
# @Time       : 2024/3/26 14:26
# @Author     : chao.li
# @Software   : PyCharm
"""


import logging
import time
from test.roku import *

import pytest

pattern_num = '033'
timing_num = '130'

# hdmirx info 预期值
hative = '1280'
wative = '800'
color_depth = 8
color_space = '0-RGB'
frame_rate = [5990, 6001]

target_pic = os.getcwd() + f'/tool/signal_generator/pattern/target_{pattern_num}.jpg'

@pytest.fixture(autouse=True, scope='session')
def setup_teardown():
	# roku_ctl.ser.start_catch_kernellog()
	roku_ctl.switch_ir('off')
	# timing_num = pattern_gener.getTimming(input='hdmi',resolution='720x480', scan_type='interlace')
	logging.info(f'timing_num {Master_8100s.get_mspg_info(timing_num)}')
	pattern_gener.setTimmingPattern(timing_num, pattern_num)
	pattern_gener.switch_ctl('hdcp', 'off')
	roku_ctl[f"tvinput.{hdmi}"].launch()
	pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')['Normal'])
	yield
	# roku_ctl.ser.stop_catch_kernellog()
	roku_ctl.switch_ir('on')
	pattern_gener.close()
	roku_ctl.home()


@pytest.fixture(scope='module', params=mode_list)
def set_picture_mode(request):
	roku_ctl.set_picture_mode(request.param)


@pytest.fixture(scope='module', params=size_list)
def set_picture_size(request):
	roku_ctl.set_picture_size(request.param)


def test_hdmirx_info():
	# input no h_freq v_freq clock resolution scan_type h_sync v_sync remark color_format color_depth hdcp hdmi_mode hdcp_mode
	# Hactive|Vactive|Color Depth|Frame Rate|TMDS clock|HDR EOTF|Dolby Vision|HDCP Debug Value|HDCP14 state|HDCP22 state
	assert roku_ctl.get_hdmirx_info(Hactive=hative, Vactive=wative, depth=str(color_depth), space=color_space,
	                                frame=frame_rate), "Hdmirx info not in expect"


@pytest.mark.skipif(skip_mode,reason='for debug')
def test_1280x800_60_mode(set_picture_mode):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_mode}_{pattern_num}_{timing_num}.jpeg'
	diff_pic = pytest.testResult.logDir + '/' + f'diff_{roku_ctl.ptc_mode}_{pattern_num}_{timing_num}.jpeg'
	roku_ctl.capture_screen(test_pic)
	pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')[roku_ctl.ptc_mode]), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)


@pytest.mark.skipif(skip_size,reason='for debug')
def test_1280x800_60_size(set_picture_size):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_size_name}_{pattern_num}_{timing_num}.jpeg'
	diff_pic = pytest.testResult.logDir + '/' + f'diff_{roku_ctl.ptc_size_name}_{pattern_num}_{timing_num}.jpeg'
	roku_ctl.capture_screen(test_pic)
	pytest.light_sensor.count_kpi(0, roku_lux.get_note(f'color_bar')['Normal']), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)
