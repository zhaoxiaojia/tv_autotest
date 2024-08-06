# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825188.py
# @Time       : 2024/6/26 16:55
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
	1.For this test case, any GIF file 8K or smaller can be used. If needed, test files are available here:
GIF
	2.Copy the test files onto a USB drive and insert the drive into the TV.
	3.Launch USB Media Player if testing unconnected mode or Roku Media Player if testing connected mode.
	4.Set the filter to show Photo files or All files.
	5.Navigate to the folder on the USB drive with the test images.

Setps:
	1.Click on any PNG image file to view it.

Expected Result:
	1.The image will be displayed correctly. There should be no distortion or wrong colors.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'FHD Vertical Test Card - 1080x1920'  # [1080X1920] gif


def test_photo_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Photo', roku_ctl.get_u_disk_file_distribution())
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
	time.sleep(1)
	roku_ctl.ir_enter('GIF', roku_ctl.get_u_disk_file_distribution())
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
