# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825155.py
# @Time       : 2024/6/4 10:34
# @Author     : chao.li
# @Software   : PyCharm
"""



import logging
import re
import time
from test.roku import *

import pytest

'''
Preconditions
	1.File Name: h264_alac.mov
	2.USB flash drive
	3.MOV video file with H.264 video

Setps:
	1.Open USB Media Player
	2.Navigate to Video tile
	3.Select your USB drive
	4.Navigate to and select your video file

Expected Result:
	1.Video and/or audio plays properly on the DUT.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()

target_file = 'h264_alac'

def test_video_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.VIDEO_STATUS_TAG,timeout=4)
	roku_ctl.catch_err('logcat.log', roku_ctl.AML_SINK_ERROR_TAG)
