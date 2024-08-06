# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825183.py
# @Time       : 2024/6/18 19:45
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
T825183-T825184

Preconditions
	1.An audio file is currently playing in the USB media player.

Setps:
	1.Press the Rewind button on the RC.

Expected Result:
	1.Pressing the RW button once should begin scanning backward through the file slowly. From that state, you must press the play button to resume playback, just as with video.
	2.The audio will rewind 30 seconds, then continue playing from there.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'Kalimba'


def test_audio_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('All', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
	time.sleep(1)
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.AUDIO_STATUS_TAG)
	time.sleep(3)
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
