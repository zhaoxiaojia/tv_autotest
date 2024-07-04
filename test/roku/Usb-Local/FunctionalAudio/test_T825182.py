# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825182.py
# @Time       : 2024/6/18 18:31
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
	1.An audio file is currently playing in the USB Media Player.

Setps:
	1.Press the Play/Pause button multiple times.

Expected Result:
	1.The audio will pause or resume playing; the icon will toggle between "Pause" and "Resume" accordingly.
	2."Start from beginning" will appear below Next and Previous once audio starts playing.    The audio will pause or resume playing; the icon will toggle between "Pause/progress bar" and "Resume" accordingly.
	3.Repeat All
	4.Shuffle
	5.Start from beginning


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
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.media_playback(target_file,
	                        roku_ctl.get_u_disk_file_distribution()), "Can't able to playback target file"
	roku_ctl.analyze_logcat(roku_ctl.AUDIO_STATUS_TAG)
	time.sleep(3)
	xml_info = roku_ctl._get_screen_xml()
	assert 'Repeat all' in xml_info,"Can't find target info"
	assert 'Shuffle' in xml_info,"Can't find target info"
	assert 'Screensaver' in xml_info,"Can't find target info"
	roku_ctl.play()
	#Todo 判断是否暂停 播放
