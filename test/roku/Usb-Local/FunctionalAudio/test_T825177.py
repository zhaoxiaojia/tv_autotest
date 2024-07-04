# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825177.py
# @Time       : 2024/6/18 17:06
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
	1.Donwload the file: sample-256kbps.mp2

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


target_file = 'sample-256kbps'


def test_audio_playback():
	roku_ctl.enter_media_player()
	roku_ctl.ir_enter('All', roku_ctl.layout_media_player_home)
	assert roku_ctl.check_udisk(), "No USB flash drive detected"
	roku_ctl.wait_for_element("Search", timeout=5)
	roku_ctl.select(time=1)
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.AUDIO_STATUS_TAG)
	time.sleep(3)