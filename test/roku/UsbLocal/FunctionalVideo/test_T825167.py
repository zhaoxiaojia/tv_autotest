# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825167.py
# @Time       : 2024/6/12 11:03
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
	1.Download the Dex3cc.mkv & the three Dex3cc .srt files: Dex3cc.eng.srt, Dex3cc.fre.srt & Dex3cc.ger.srt from: Dex3cc Both the video and srt files must be copied to the same directory.
	2.NOTE - You will NOT see French and German rendered when these tracks are selected, this merely demonstrates that we can utilize .srt files for captioning/subtitles

Setps:
	1.Copy the Dex3cc.mkv file to a USB drive and insert that drive into the TV under test
	2.Launch Roku Media Player and choose video. Select the Dec3cc.mkv file
	3.Enable Closed Captioning via the Options menu ( * )
	4.Let text render using default track
	5.Bring up the Options menu and in Captioning track select French
	6.Bring up the Options menu and in Captioning track select German

Expected Result:
	1.Video and/or audio plays properly on the DUT.
	2.Caption text should be rendered. Captions should be displayed immediately. There should be no delay before the captions start.
	3.French should be an option in the Captioning track field. Once selected, text should be rendered*
	4.German should be an option in the Captioning track field. Once selected, text should be rendered*
	5.*NOTE: You will NOT see French or German rendered when these tracks are selected. You should see English sentences rendered for each of the selected tracks.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'Dex3cc'


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
	roku_ctl.play(time=1)
	roku_ctl.set_caption_status('On always')
	for i in ['German', 'French','English']:
		# Todo 切换 字幕， 目前暂无手段检测到字幕
		roku_ctl.set_caption(i)
		roku_ctl.back(time=1)
		roku_ctl.back(time=1)
		roku_ctl.reverse(time=1)
		roku_ctl.reverse(time=1)
		time.sleep(2)
		roku_ctl.play(time=1)
