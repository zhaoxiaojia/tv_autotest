# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825141.py
# @Time       : 2024/5/29 10:16
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import time
from test.roku import *

import pytest

'''
Setps:
	1.In USB Media Player or Roku Media Player, on the Select Media Device page, press the * button.
	2.In the Help & Settings pop-up menu, select Help.
	3.Navigate up and down the page tiles and verify that the text changes accordingly.
	4.Press the Back button to exit.     

Expected Result:
	1.The Help pages open, navigate, and close correctly.

'''

help_description = [
	'To play or view content from',
	'To view or play a file, first select a Media Type from the main screen.',
	'To search your USB or DLNA server, press * on the remote and select Search.',
	'Press OK on a media file to play or view that file. Press PLAY on a folder or playlist to play the contents.',
	'The following media formats are supported',
	'Playlists are supported in the .m3u and .',
	'DTS is supported via passthrough on MKV.'
]


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()

def test_help_setting_display():
	roku_ctl.enter_media_player()
	roku_ctl.info(time=1)
	roku_ctl.ir_enter('Help', roku_ctl.layout_media_player_help_setting)
	if 'Searching Media' not in roku_ctl._get_screen_xml():
		help_description.pop(2)
	for i in help_description:
		assert i in roku_ctl._get_screen_xml(), "Help description not expected"
		roku_ctl.down(time=2)
