# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825166.py
# @Time       : 2024/6/7 11:24
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
	1.Copy the h264_aac_Subtitles.mkv
	2.Copy the file to a USB drive

Setps:
	1.Insert the USB drive with the h264_aac_Subtitles.mkv file on it
	2.Launch Roku Media Player and select Video
	3.Let the h264_aac_Subtitles.mkv file play
	4.Push the * button
	5.Set Closed Captioning to On
	6.Rewind to the beginning of the video
	7.Set Captioning track to Hungarian & allow caption text to be rendered
	8.Rewind to the beginning of the video
	9.Set Captioning track to German & allow caption text to be rendered
	10.Rewind to the beginning of the video
	11.Set Captioning track to French & allow caption text to be rendered
	12.Rewind to the beginning of the video
	13.Set Captioning track to Spanish & allow caption text to be rendered
	14.Rewind to the beginning of the video
	15.Set Captioning track to Italian & allow caption text to be rendered
	16.Rewind to the beginning of the video
	17.Set Captioning track to Japanese & allow caption text to be rendered
	18.Rewind to the beginning of the video
	19.Set Captioning track to Unknown language & allow caption text to be rendered

Expected Result:
	1.The audio that plays by default is the commentary on the scene. the aim is to check the caption change based on the original video track.
	2.English caption text should be rendered
	3.Hungarian caption text should be rendered
	4.German caption text should be rendered
	5.French caption text should be rendered
	6.Spanish caption text should be rendered
	7.Italian caption text should be rendered
	8.We don't support the font set needed for Japanese so you'll see rectangles, periods and pipe character " | "
	9.You'll see a series of characters (mainly lower case a) with different accent marks
	10.*NOTE: You will NOT see French or German rendered when these tracks are selected. You should see English sentences rendered for each of the selected tracks.



'''

@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'h264_aac_Subtitles'


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
	for i in ['Hungarian', 'German', 'French', 'Spanish', 'Italian', 'Japanese', 'Other','English']:
		# Todo 切换 字幕， 目前暂无手段检测到字幕
		roku_ctl.set_caption(i)
		roku_ctl.back(time=1)
		roku_ctl.back(time=1)
		roku_ctl.reverse(time=1)
		roku_ctl.reverse(time=1)
		time.sleep(2)
		roku_ctl.play(time=1)
