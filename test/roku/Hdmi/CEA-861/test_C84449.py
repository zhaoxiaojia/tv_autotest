# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_C84449.py
# @Time       : 2024/3/25 11:30
# @Author     : chao.li
# @Software   : PyCharm
"""


import logging
import time
from test.roku import *

import pytest

pattern_num = '033'
timing_num = '459'

# hdmirx info 预期值
hative = '1920'
wative = '2160'
color_depth = 8
color_space = '3-YUV420'
frame_rate = [5900, 6101]

target_pic = os.getcwd() + f'/tool/signal_generator/pattern/target_{pattern_num}.jpg'


@pytest.fixture(autouse=True, scope='session')
def setup_teardown():
	# roku_ctl.ser.start_catch_kernellog()
	 
	# timing_num = pytest.pattern_gener.getTimming(input='hdmi',resolution='720x480', scan_type='interlace')
	logging.info(f'timing_num {Master_8100s.get_mspg_info(timing_num)}')
	pytest.pattern_gener.setTimmingPattern(timing_num, pattern_num)
	roku_ctl[f"tvinput.{hdmi}"].launch()
	if pytest.light_sensor:
		pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')['Normal'])
	time.sleep(15)
	yield
	# roku_ctl.ser.stop_catch_kernellog()
	roku_ctl.home()
	roku_ctl.get_dmesg_log()
	pytest.pattern_gener.close()



@pytest.fixture(scope='module')
def set_picture_mode(request):
	roku_ctl.set_picture_mode(mode_list)


@pytest.fixture(scope='module')
def set_picture_size(request):
	roku_ctl.set_picture_size(size_list)


def test_hdmirx_info():
	# input no h_freq v_freq clock resolution scan_type h_sync v_sync remark color_format color_depth hdcp hdmi_mode hdcp_mode
	# Hactive|Vactive|Color Depth|Frame Rate|TMDS clock|HDR EOTF|Dolby Vision|HDCP Debug Value|HDCP14 state|HDCP22 state
	assert roku_ctl.get_hdmirx_info(Hactive=hative, Vactive=wative, depth=str(color_depth), space=color_space,
	                                frame=frame_rate), "Hdmirx info not in expect"


@pytest.mark.skipif(skip_mode,reason='for debug')
def test_4kp60_mode(set_picture_mode):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_mode}_{pattern_num}_{timing_num}.jpeg'
	diff_pic = pytest.testResult.logDir + '/' + f'diff_{roku_ctl.ptc_mode}_{pattern_num}_{timing_num}.jpeg'
	pytest.pattern_gener.switch_ctl('hdcp', 'off')
	roku_ctl.capture_screen(test_pic)
	pytest.pattern_gener.switch_ctl('hdcp', 'on')
	if pytest.light_sensor:
		pytest.light_sensor.count_kpi(0, roku_lux.get_note('color_bar')[roku_ctl.ptc_mode]), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)



@pytest.mark.skipif(skip_size,reason='for debug')
def test_4kp60_size(set_picture_size):
	test_pic = pytest.testResult.logDir + '/' + f'test_{roku_ctl.ptc_size}_{pattern_num}_{timing_num}.jpeg'
	diff_pic = pytest.testResult.logDir + '/' + f'diff_{roku_ctl.ptc_size}_{pattern_num}_{timing_num}.jpeg'
	pytest.pattern_gener.switch_ctl('hdcp', 'off')
	roku_ctl.capture_screen(test_pic)
	pytest.pattern_gener.switch_ctl('hdcp', 'on')
	if pytest.light_sensor:
		pytest.light_sensor.count_kpi(0, roku_lux.get_note(f'color_bar')['Normal']), 'Not in expect'
	pil.compare_images(test_pic, target_pic, diff_pic)

