# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825190.py
# @Time       : 2024/6/28 17:09
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
include 
T825190~T825191

Preconditions
	1.A photo is being viewed in the USB Media Player.

Setps:
	1.Press the Rewind button on the remote.
	2.Press the D-Pad Left Arrow button. 

Expected Result:
	1.Pressing Rewind or Left Arrow will navigate to the previous photo. 
	2.Pressing D-Pad Left Arrow will navigate to the previous photo.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'leaves'


def test_photo_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Photo', roku_ctl.get_u_disk_file_distribution())
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	for i in range(10):
		xml_info = roku_ctl._get_screen_xml()
		if 'hudTitle' in xml_info and target_file in xml_info:
			time.sleep(3)
			break
		time.sleep(1)
	else:
		assert False, "Can't display target photo"
	roku_ctl.right(time=5)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and target_file not in xml_info, "File shouldn't be changed"
	roku_ctl.left(time=5)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and target_file in xml_info, "File should be changed"
	roku_ctl.reverse(time=5)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and target_file not in xml_info, "File shouldn't be changed"
	roku_ctl.forward(time=5)
	xml_info = roku_ctl._get_screen_xml()
	assert 'hudTitle' in xml_info and target_file in xml_info, "File should be changed"
