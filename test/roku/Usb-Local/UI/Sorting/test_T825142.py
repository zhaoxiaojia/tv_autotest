# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825142.py
# @Time       : 2024/5/29 11:01
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import time
from test.roku import *

import pytest

'''
include 

T825142 - T825144

Setps:
	1.Open USB Media Player
	2.Navigate to Video, Audio, or Photo tile
	3.Select your USB drive
	4.Press * button on remote
	5.Highlight the Sort option
	6.Press OK button on remote to cycle to Default
	7.Highlight OK and select to apply the new sorting
	8.Press OK button on remote to cycle to A→Z.
	9.Highlight OK and select to apply the new sorting.
	10.Press OK button on remote to cycle to Z→A.
	11.Highlight OK and select to apply the new sorting.

Expected Result:
	1.Your files and folders should now be sorted by track number.
	2.File that do not contain track number, will be sorted by the order in which they come back from the USB drive's file system.
This is determined by the order in which the files were written to the corresponding directory.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
	yield
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
	roku_ctl.home(time=1)
	roku_ctl.get_dmesg_log()


def test_file_sort_default_sort():
	roku_ctl.enter_media_player()
	for i in ['Video', 'Audio', 'Photo']:
		roku_ctl.ir_enter(i, roku_ctl.media_player_home)
		roku_ctl.select(time=1)
		for _ in range(3):
			temp = roku_ctl.get_u_disk_file_distribution()
			roku_ctl.info(time=1)
			for _ in range(5):
				if 'Sort' in roku_ctl.ir_current_location:
					break
				roku_ctl.down(time=1)
				roku_ctl.get_ir_focus()
			roku_ctl.select(time=1)
			for _ in range(5):
				if 'OK' in roku_ctl.ir_current_location:
					break
				roku_ctl.down(time=1)
				roku_ctl.get_ir_focus()
			roku_ctl.select(time=1)
			sort_list = roku_ctl.get_u_disk_file_distribution()
			logging.info(f'切换排序前 {[i for arr in temp for i in arr]}')
			logging.info(f'切换排序后 {[i for arr in sort_list for i in arr]}')
			assert temp[0] != sort_list[0] and temp[-1] != sort_list[-1], "File list should not be the same"
		roku_ctl.back(time=1)
		roku_ctl.back(time=1)
