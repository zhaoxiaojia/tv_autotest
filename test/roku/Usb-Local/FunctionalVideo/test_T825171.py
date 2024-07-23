# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825171.py
# @Time       : 2024/6/14 14:00
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
	1.A USB drive with HDR videos is available.
	2.Download -hdr10.mp4
	3.For 2K TV, download:-LG_Chess_HDR_2K_1920_1080_HDR10

Setps:
	1.Play *.mp4 files via USB media player.
	2.Perform Pause, Play/Resume, FFW and RW trick plays.


Expected Result:
	1.Video starts cleanly with audio and video in sync. Video has no garbage/tearing issue from beginning to end.
	2.Verify after resuming from pause and seeking that video continues cleanly.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	roku_ctl.home(time=2)
	roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
	roku_ctl.ir_enter('TV picture settings', roku_ctl.get_launcher_element('ArrayGridItem'))
	for _ in range(10):
		roku_ctl.get_ir_focus()
		if 'HDR notification' in roku_ctl.ir_current_location:
			roku_ctl.select(time=1)
			if 'On' != roku_ctl.get_ir_focus():
				roku_ctl.down(time=1)
			roku_ctl.select(time=1)
			break
		roku_ctl.down(time=1)
	else:
		logging.warning("Can't find HDR setting")
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'LG_Chess_HDR_2K_1920_1080_HDR10'


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
