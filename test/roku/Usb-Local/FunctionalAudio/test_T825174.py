# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825174.py
# @Time       : 2024/6/18 16:50
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
	1.Download the file: dolby digital ac3
	2.USB flash drive
	3.AC3 audio file with AC-3 (Dolby Digital) audio

Setps:
	1.Open USB Media Player
	2.Navigate to Audio tile
	3.Select your USB drive
	4.Navigate to and select your audio file

Expected Result:
	1.Audio plays properly on the DUT.


'''


@pytest.fixture(autouse=True)
def setup_teardown():

	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'dolby digital ac3'


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