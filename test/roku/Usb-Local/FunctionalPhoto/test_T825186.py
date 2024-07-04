# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825186.py
# @Time       : 2024/7/1 17:36
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
	1.For this test case, any JPEG file can be used. If needed, test files are available here:
[JPEG](Shared Documents> images> Image Test Files> JPEG
	2.Copy the test files onto a USB drive and insert the drive into the TV.
	3.Launch USB Media Player if testing unconnected mode or Roku Media Player if testing connected mode.
	4.Set the filter to show Photo files or All files.
	5.Navigate to the folder on the USB drive with the test images.

Setps:
	1.Click on any JPEG image file to view it.

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


target_file = 'Test Card - 7660x4340'  # [7660x4340] png


def test_photo_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Photo', roku_ctl.get_u_disk_file_distribution())
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter('JPEG', roku_ctl.get_u_disk_file_distribution())
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
