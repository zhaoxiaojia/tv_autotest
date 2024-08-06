# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/26 11:13
# @Author  : chao.li
# @File    : test_T1186007.py




import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''
include T1186007~T1186012

Preconditions
    1. Highlight Roku Home -> Settings -> System -> About menu item
    2. Review the right part of the screen.

Setps:
	1. Right part of the screen should contain the graphical artifacts.
	2. Under the the graphical artifacts verify:
        the name given to the TV during the linking phase
        account information (if the TV is in the connected mode)

Expected Result:
	1. After selecting About, should see 'System' at the top of the screen after Roku

'''


graphical_info = 'about.webp'
account_info = 'uiElementId="device-account"'
ipaddress_re = r'uiElementId="ip-address-value".*?\"(\d+\.\d+\.\d+\.\d+)\"'
wired_mac_re = r'uiElementId="wired-mac-addr-value".*?\"(\w+:\w+:\w+:\w+:\w+:\w+)\"'
wireless_mac_re = r'uiElementId="wireless-mac-addr-value".*?\"(\w+:\w+:\w+:\w+:\w+:\w+)\"'
microsd_info = 'MicroSD Card'
network_name_info = 'uiElementId="network-name-value"'

@pytest.fixture(autouse=True)
def setup_teardown():
    roku_ctl.home(time=2)
    roku_ctl.home(time=1)
    yield
    roku_ctl.home(time=1)
    roku_ctl.home(time=1)
    roku_ctl.get_dmesg_log()


def test_about():
    home_launcher = roku_ctl.get_launcher_element('LabelListNativeItem')
    account = 'What to Watch' in home_launcher
    roku_ctl.ir_enter('Settings', home_launcher)
    roku_ctl.ir_enter('System', roku_ctl.get_launcher_element('ArrayGridItem'))
    roku_ctl.ir_navigation('About', roku_ctl.get_launcher_element('ArrayGridItem'))
    time.sleep(1)
    xml_info = roku_ctl._get_screen_xml()
    # 检测 about 信息 包括图片的显示 账号显示
    assert graphical_info in xml_info,"Should display graphical artifacts"
    if account:
        assert account_info in xml_info,"Should display account display"
    roku_ctl.select(time =1)

    xml_info = roku_ctl._get_screen_xml()
    ipaddress = re.findall(ipaddress_re,xml_info,re.S)
    # 检测 ip地址  暂不能处理 断开网络的场景
    assert ipaddress[0],"Should display ip address"
    # 检测 sd 卡
    assert  microsd_info not in xml_info,"Shouldn't display sd info"
    # 检测网路名字  不支持 无网络和 wifi连接场景
    assert network_name_info not in xml_info,"Shouldn't display network name"
    # 检测 wired mac 地址
    wired_mac = re.findall(wired_mac_re,xml_info,re.S)
    assert wired_mac[0],"Should display wired mac address"
    # 检测 wireless mac 地址
    wireless_mac = re.findall(wireless_mac_re,xml_info,re.S)
    assert wireless_mac[0],"Should display wireless mac address"
