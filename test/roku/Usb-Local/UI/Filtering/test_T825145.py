# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825145.py
# @Time       : 2024/5/30 11:17
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import time
from test.roku import *

import pytest

'''
include 

T825145 - T825147

Setps:
	1.Open USB Media Player
	2.Navigate to Video, Audio, or Photo tile
	3.Select your USB drive
	4.Press * button on remote
	5.Highlight the Media type option
	6.Press OK button on remote to cycle to Videos
	7.Highlight OK and select to apply the new filter
	8.Press OK button on remote to cycle to Audio
	9.Highlight OK and select to apply the new filter
	10.Press OK button on remote to cycle to Photos
	11.Highlight OK and select to apply the new filter

Expected Result:
	1.When pressing *, you should see Videos (active) and also if you are inside any of the folder which has all the media files(video, audio &, image) only video files should be seen
	2.Changing filter to another option show lead to Videos no longer being active.
	3.NOTE: The following file types will be displayed:
3g2, 3gp, asf, flv, lrv, m2ts, m3u8, mv4, mkv, mov, mp4, mts, trp, ts
The m3u playlist will be displayed on the top line with the folders regardless of the media type being viewed.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


def test_file_type():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.media_player_home)
	roku_ctl.select(time=1)
	for i in ['audio', 'image', 'video']:
		roku_ctl.info(time=1)
		for _ in range(5):
			if 'Media type' in roku_ctl.ir_current_location:
				break
			roku_ctl.down(time=1)
			roku_ctl.get_ir_focus()
		roku_ctl.select(time=1)
		if 'Media type - [All]' in roku_ctl._get_screen_xml():
			roku_ctl.select(time=1)
		for _ in range(5):
			if 'OK' in roku_ctl.ir_current_location:
				break
			roku_ctl.down(time=1)
			roku_ctl.get_ir_focus()
		roku_ctl.select(time=1)
		dumpsys = roku_ctl._get_screen_xml()
		type_list = set(re.findall(r'poster_(.*?)_fhd', dumpsys))
		assert type_list == {'folder', i}, "Able to see another type file in list, not expected"
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
