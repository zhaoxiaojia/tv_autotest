# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825138.py
# @Time       : 2024/4/29 16:06
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import time
from test.roku import *

import pytest

'''
Setps:
	1.Open USB Media Player
	2.Navigate to Video tile
	3.Select your USB drive

Expected Result:
	1.On selecting Video tile, USB Drive/Media Server should be displayed (Note: DLNA media servers on the same network will also be displayed when in connected mode)
	2.You should only see folders and video files.
	3.You are able to select and play video files.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'aac'
target_file_set = {'folder', 'video'}


def test_video_tile():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	dumpsys = roku_ctl._get_screen_xml()
	type_list = set(re.findall(r'poster_(.*?)_fhd', dumpsys))
	assert type_list == target_file_set, "Able to see another type file in list, not expected"
	assert roku_ctl.ir_navigation(target_file,
	                              roku_ctl.get_u_disk_file_distribution()), "Can't able to location target file"
