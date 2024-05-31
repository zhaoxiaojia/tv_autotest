# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_demo.py
# @Time       : 2024/4/26 14:41
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import time
from test.roku import *

import pytest


@pytest.fixture(autouse=True)
def tear_down():
	yield
	roku_ctl.catch_err('logcat.log', roku_ctl.AML_SINK_ERROR_TAG)


def get_info():
	width = pytest.executer.checkoutput(command.show_video_width)
	height = pytest.executer.checkoutput(command.show_video_height)
	frame = pytest.executer.checkoutput(command.show_frame_decoded)
	frame_rate = pytest.executer.checkoutput(command.show_frame_rate)
	logging.info(f'width : {width}\n height : {height}\n frame : {frame}\n frame_rate : {frame_rate}\n')


def test_demo():
	pytest.executer.execute_cmd('logcat -c')
	roku_ctl.select(time=1)
	get_info()
	roku_ctl.analyze_logcat(roku_ctl.VIDEO_STATUS_TAG, timeout=600)
