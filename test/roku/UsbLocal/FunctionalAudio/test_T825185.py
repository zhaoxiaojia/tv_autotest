# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825185.py
# @Time       : 2024/6/24 21:36
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
	1.An audio file is currently playing in the USB media player.


Setps:
	1.Tap the D-pad left or right arrow buttons on the RC.
	2.Press and hold the D-pad left or right arrow buttons on the RC. 

Expected Result:
	1.Pressing D pad skips to previous or next file.
	2.Holding the button will rewind or fast-forward through the file.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'ac3-48000-200-st'


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
	roku_ctl.right(time=1)
	assert roku_ctl.get_ir_focus(secret=True)!= target_file,"Switch file failed"
