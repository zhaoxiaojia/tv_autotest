# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825170.py
# @Time       : 2024/6/14 14:14
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
	1.The TV is capable of playing Dolby Vision
	2.A USB drive with a Dolby Vision video is available
	3.Settings | TV picture settings | Dolby Vision notification is set to On. Note: on Dolby Vision capable TVs, this label will only say Dolby Vision notification, but will affect all HDR formats

Setps:
	1.Play Dolby Vision content from the USB drive (Roku/USB Media Player)
	2.Perform some trick-play operations during playback: seek forward, rewind, replay, etc.
	3.Press the 'Back' button to exit playback, then restart the Dolby Vision video


Expected Result:
	1.Step 1: Dolby Vision notification will appear in the upper right corner when playback begins
	2.Step 2: Trick play does not cause the Dolby Vision notification to reappear
	3.Step 3: Dolby Vision notification will appear when playback is restarted


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	roku_ctl.home(time=2)
	roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
	roku_ctl.ir_enter('TV picture settings', roku_ctl.get_launcher_element('ArrayGridItem'))
	for _ in range(10):
		roku_ctl.get_ir_focus()
		if 'Dolby Vision notification' in roku_ctl.ir_current_location:
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


target_file = 'DV-demo'
dv_logo = 'Dolby_vision_VertLogo'

@pytest.mark.skip()
def test_video_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('Video', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
	time.sleep(1)
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	for _ in range(5):
		if dv_logo in roku_ctl._get_screen_xml():
			assert True
			break
		time.sleep(1)
	else:
		assert False, "Dolby Vision info doesn't display"
	time.sleep(5)
	roku_ctl.forward()
	roku_ctl.forward()
	roku_ctl.play(time=3)
	assert dv_logo not in roku_ctl._get_screen_xml(), "Dolby Vision info shouldn't display"
	roku_ctl.back(time=1)
	roku_ctl.select(time=1)
	for _ in range(5):
		if dv_logo in roku_ctl._get_screen_xml():
			assert True
			break
		time.sleep(1)
	else:
		assert False, "Dolby Vision info doesn't display"
