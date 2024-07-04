# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825148.py
# @Time       : 2024/5/30 13:40
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
	1.Play content on USB Input
	2.Navigate to Video, Audio, or Photo tile
	3.Make changes or toggle through all Local Settings settings (if applicable):
Picture Mode
		3.1.Picture Mode
		3.2.Picture Size
		3.3.All Advanced Picture Settings
	4.Validate Expected Result
	5.Go to any other Input
	6.Validate Expected Result

Expected Result:
	1.Validated that Picture Mode, Picture Size and Advanced Picture Settings are working properly
	2.Validated that Local Settings are Only applied to selected Input on step 1
	3.The * label should be displayed next to picture mode once the settings changed from default values
	4.note: Changes on Advanced Picture Settings may not work before we get PQ data from the factory

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'bbb-4mbps-24fps.h264.ac3'


def test_picture_size_mode():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.layout_media_player_home)
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter(target_file, roku_ctl.get_u_disk_file_distribution())
	if 'Play from beginning' in roku_ctl._get_screen_xml():
		roku_ctl.down(time=1)
	roku_ctl.select(time=1)
	time.sleep(5)
	roku_ctl.set_picture_mode(mode_list)
	time.sleep(1)
	roku_ctl.set_picture_size(size_list)
	roku_ctl.back(time=1)
