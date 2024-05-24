# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_T825138.py
# @Time       : 2024/4/29 16:06
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import time
from test.roku import *

import pytest


@pytest.fixture(autouse=True, scope='session')
def setup_teardown():
	yield


# roku_ctl.home()
# roku_ctl.get_dmesg_log()


def test_video_tile():
	# roku_ctl.enter_media_player()
	array = roku_ctl.get_u_disk_file_distribution()
	logging.info(array)
	roku_ctl.ir_navigation('hdr10', array)
