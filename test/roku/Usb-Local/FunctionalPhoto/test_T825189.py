# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825189.py
# @Time       : 2024/6/27 16:33
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''

Preconditions
	1.A photo is being viewed in the USB Media Player.

Setps:
	1.Press the Play/Pause button on the remote a few times.

Expected Result:
	1.Pressing Play/Pause will pause or resume the photo slideshow.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = '3840x2160'


def test_photo_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Photo', roku_ctl.get_u_disk_file_distribution())
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
	time.sleep(1)
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	for i in range(10):
		xml_info = roku_ctl._get_screen_xml()
		if 'hudTitle' in xml_info and target_file in xml_info:
			time.sleep(0.5)
			break
	else:
		assert False, "Can't display target photo"
	logging.info('Photo is display')
	logging.info('Pause')
	roku_ctl.play(time=1)
	time.sleep(15)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and f'text="{target_file}"' in xml_info, "File shouldn't be changed"
	logging.info('Resume')
	roku_ctl.play(time=1)
	time.sleep(15)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and f'text="{target_file}"' not in xml_info, "File should be changed"
