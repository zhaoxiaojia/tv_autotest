# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/25 9:58
# @Author  : chao.li
# @File    : test_T1249494.py


import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''
include T1221075、T1187964、T1187965

Preconditions
    1. Roku TV only
    2. Must have valid internet connection and the TV must be currently connected
    3. Must have valid and active Roku account and have the TV linked to this account - Streams to use:
        US:Qubo_Spa
        BR:EiTV_Parental-Sample
        UK:psb1-bbca-522mhz-20220925
        DE:DE_Parental01_v0.1
        AU:AUS_Parental_01 Must have Parental Controls enabled.


Setps:
	1. Select Settings
	2. Select System
	3. Select Control other devices (CEC)
	4. Select Search for CEC devices

Expected Result:
	1. "CEC devices" dialog is displayed with "Update CEC device list" and "Cancel " options

'''


@pytest.fixture(autouse=True)
def setup_teardown():
    roku_ctl.home(time=1)
    roku_ctl.home(time=1)
    roku_ctl.right(time=1)
    roku_ctl.right(time=1)
    roku_ctl.down(time=1)
    roku_ctl.down(time=1)
    if 'ABC World News Now' in roku_ctl._get_screen_xml():
        logging.info('aaaaaa')
        roku_ctl.down(time=1)
    roku_ctl.info(time=1)
    roku_ctl.select(time=1)
    if 'A Better Smart TV Experience from Roku!' in roku_ctl._get_screen_xml():
        roku_ctl.select(time=1)
    roku_ctl.wait_for_element('Antenna')
    roku_ctl.down(time=1)
    roku_ctl.select(time=1)
    roku_ctl.wait_for_element("Watch live TV",timeout=120)
    roku_ctl.select(time=1)
    if 'More free TV!' in roku_ctl._get_screen_xml():
        roku_ctl.select(time=1)
    yield
    roku_ctl.home(time=1)
    roku_ctl.home(time=1)
    roku_ctl.get_dmesg_log()


device_info_tag = 'HDMI '

search_info_tag = 'Search for CEC devices'
touch_info_tag = '1-touch play'
standby_info_tag = 'System standby'

update_info_tag = 'uiElementId="update-device-list"'
cancel_info_tag = 'uiElementId="cancel"'


@pytest.mark.skip
def test_cec():
    roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
    roku_ctl.ir_enter('System', roku_ctl.get_launcher_element('ArrayGridItem'))
    roku_ctl.ir_enter('Control other devices (CEC)', roku_ctl.get_launcher_element('ArrayGridItem'))
    time.sleep(2)
    xml_info = roku_ctl._get_screen_xml()
    # T1187964 检测点
    assert device_info_tag in xml_info, "CEC device info can't be found"
    # T1187965 监测点
    assert search_info_tag in xml_info, f"{search_info_tag} can't be found"
    assert touch_info_tag in xml_info, f"{search_info_tag} can't be found"
    assert standby_info_tag in xml_info, f"{search_info_tag} can't be found"
    roku_ctl.select(time=2)
    xml_info = roku_ctl._get_screen_xml()
    # T1221075 检测点
    assert update_info_tag in xml_info and cancel_info_tag in xml_info


