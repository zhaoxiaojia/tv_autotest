# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825162.py
# @Time       : 2024/6/5 11:04
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
	1.USB flash drive with various video files. (**Note:** Rewind and fast-forward on TS streams is not supported.)

Setps:
	1.Open USB Media Player.
	2.Navigate to Video tile.
	3.Select your USB drive.
	4.Navigate to and select your file.
	5.Press the Fast-Forward button on the remote during video playback.
	6.Press the Rewind button on the remote during video playback.

Expected Result:
	1.Pressing the rewind button will rewind the video. Pressing it multiple times will speed up the rewind.
	2.Upon rewinding the video, a seek bar should appear.

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
	roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
	time.sleep(1)
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.VIDEO_STATUS_TAG)
	roku_ctl.forward()
	roku_ctl.forward()
	time.sleep(2)
	roku_ctl.play()
	assert roku_ctl._get_media_process_bar() > 5, "Fast forward did not take effect"
	roku_ctl.reverse()
	roku_ctl.reverse()
	time.sleep(2)
	roku_ctl.play()
	assert roku_ctl._get_media_process_bar() < 180, "Back forward did not take effect"
	roku_ctl.catch_err('logcat.log', roku_ctl.AML_SINK_ERROR_TAG)
