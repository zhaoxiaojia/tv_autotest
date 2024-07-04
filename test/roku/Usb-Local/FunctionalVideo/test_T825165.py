# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825165.py
# @Time       : 2024/6/5 15:39
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
	1.A video file is currently playing in the USB media player. (**Note:** Rewind and fast-forward on TS streams is not supported.)


Setps:
	1.Press the Jump Back (Replay) button on the remote.

Expected Result:
	1.The video will jump back 20 seconds, then continue playing from there.
	2.The seek bar will appear.


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
	roku_ctl.forward()
	roku_ctl.forward()
	time.sleep(2)
	roku_ctl.play()
	roku_ctl.replay(time=1)
	temp = roku_ctl._get_media_process_bar()
	roku_ctl.replay(time=1)
	index = roku_ctl._get_media_process_bar()
	assert temp - index in range(18, 23), "Replay did not take effect"
	roku_ctl.catch_err('logcat.log', roku_ctl.AML_SINK_ERROR_TAG)
