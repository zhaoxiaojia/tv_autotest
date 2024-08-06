# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 13:45
# @Author  : chao.li
# @Site    : 
# @File    : test_T1221075.py
# @Software: PyCharm 
# @Comment :


import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''
include T1221075、T1187964、T1187965
Preconditions
    1. TV only
    2. Device is linked to Roku account - CEC compatible Device(Roku STB) connected to HDMI 1
    3. Start from Home screen
    
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
    roku_ctl.home(time=2)
    roku_ctl.home(time=1)
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


def test_cec():
    roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
    roku_ctl.ir_enter('System', roku_ctl.get_launcher_element('ArrayGridItem'))
    roku_ctl.ir_enter('Control other devices (CEC)', roku_ctl.get_launcher_element('ArrayGridItem'))
    time.sleep(2)
    xml_info = roku_ctl._get_screen_xml()
    # T1187964 检测点
    assert device_info_tag in xml_info , "CEC device info can't be found"
    # T1187965 监测点
    assert search_info_tag in xml_info ,f"{search_info_tag} can't be found"
    assert touch_info_tag in xml_info ,f"{search_info_tag} can't be found"
    assert standby_info_tag in xml_info ,f"{search_info_tag} can't be found"
    roku_ctl.select(time=2)
    xml_info = roku_ctl._get_screen_xml()
    # T1221075 检测点
    assert update_info_tag in xml_info and cancel_info_tag in xml_info


