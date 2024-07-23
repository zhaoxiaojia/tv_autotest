# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825168.py
# @Time       : 2024/6/12 11:10
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
	1.Download the test file: Big_Buck_Bunny_MKV_Multi_Subs_30_FPS
	2.Copy the file to a USB drive and plug that drive into the TV.

Setps:
	1.Play the video file via Roku Media Player 
	2.Ensure that captions are enabled ('*' Options Menu > Accessibility & language > Closed captioning > On always) 
	3.Cycle through and test each of the available caption language (English, Chinese, Chinese, Other)

Expected Result:
	1.'English' captioning track should be shown
	2.'Chinese' captioning tracks should render as rectangles with an X through them (English char are shown) 
	3.'Other' captioning track should be rendered with rectangles on top line & English on the bottom line/s
	4.Caption text should begin rendering using the newly selected track within 12 seconds. We don't support the font needed for Chinese language so captions will be rendered as rectangles with a X through them.
	5.The subtitles have no connection to the video; they're just for testing purposes.


'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


target_file = 'Big_Buck_Bunny_MKV_Multi_Subs_30_FPS'


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
	for i in ['Chinese', 'English','Other']:
		# Todo 切换 字幕， 目前暂无手段检测到字幕
		roku_ctl.set_caption(i)
		roku_ctl.back(time=1)
		roku_ctl.back(time=1)
		roku_ctl.reverse(time=1)
		roku_ctl.reverse(time=1)
		time.sleep(2)
		roku_ctl.play(time=1)
