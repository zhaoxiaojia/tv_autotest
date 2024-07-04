# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825164.py
# @Time       : 2024/6/5 13:35
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
T825162 & T825163

Preconditions
	1.Note: Rewind and fast-forward on TS streams is not supported.


Setps:
	1.Launch the Roku Media Player (RMP)
	2.Start playback of a video that is over 5 minutes.
	3.Tap the D-pad left or right arrow buttons on the RC.
	4.Press and hold the D-pad left or right arrow buttons on the RC.

Expected Result:
	1.Tapping the buttons moves the current playback position back or forward by 5 seconds.
	2.Holding the button will rewind or fast-forward through the file.


Ps:
Not able to hold buitton
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


def test_video_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.VIDEO_STATUS_TAG)
	roku_ctl.right(time=1)
	roku_ctl.right(time=1)
	roku_ctl.play()
	assert roku_ctl._get_media_process_bar() > 5, "Right did not take effect"
	roku_ctl.left(time=1)
	roku_ctl.left(time=1)
	roku_ctl.play()
	assert roku_ctl._get_media_process_bar() < 15, "Left did not take effect"
	roku_ctl.catch_err('logcat.log', roku_ctl.AML_SINK_ERROR_TAG)
