# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : __init__.py.py
# @Time       : 2024/4/29 16:05
# @Author     : chao.li
# @Software   : PyCharm
"""
import logging

import pytest
from test.roku import *


# 将排序方式 设置成short
logging.info('Set Row Style to Short')
roku_ctl.enter_media_player()
roku_ctl.ir_enter('Audio', roku_ctl.layout_media_player_home)
assert roku_ctl.check_udisk(), "No USB flash drive detected"
roku_ctl.wait_for_element("Search", timeout=5)
roku_ctl.select(time=1)
roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
time.sleep(1)
roku_ctl.info(time=1)
if 'Row Style - [Short]' not in roku_ctl._get_screen_xml():
	for _ in range(7):
		if 'Row Style' not in roku_ctl.get_ir_focus(secret=True):
			roku_ctl.down(time=1)

	for _ in range(5):
		if 'Short' not in roku_ctl.get_ir_focus(secret=True):
			roku_ctl.select(time=1)

	roku_ctl.down(time=1)
	roku_ctl.select(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
roku_ctl.home(time=1)
