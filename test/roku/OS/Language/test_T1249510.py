# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/25 10:02
# @Author  : chao.li
# @File    : test_T1249510.py



import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''
include T1249510、T1249509

Preconditions
    1. Device is linked to Roku account
    2. Language is set to any option except English, e.g. Spanish (Settings | System | Language | Español)
    3. Start from Home screen

Setps:
	1. Select Settings
	2. Select System
	3. Select Language
	4. Select English

Expected Result:
	1. The UI text should switch to the English language

'''


@pytest.fixture(autouse=True)
def setup_teardown():
    roku_ctl.home(time=2)
    roku_ctl.home(time=1)
    yield
    roku_ctl.home(time=1)
    roku_ctl.home(time=1)
    roku_ctl.get_dmesg_log()


english_language_tag = 'text="Language"'
espanol_language_tag = 'text="Idioma"'

def test_cec():
    roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
    roku_ctl.ir_enter('System', roku_ctl.get_launcher_element('ArrayGridItem'))
    roku_ctl.ir_enter('Language', roku_ctl.get_launcher_element('ArrayGridItem'))
    time.sleep(2)
    roku_ctl.ir_enter(u'Espa\xf1ol', roku_ctl.get_launcher_element('RadioButtonItem')[:12])
    for i in range(30):
        xml_info = roku_ctl._get_screen_xml()
        if espanol_language_tag in xml_info:
            break
        time.sleep(10);
    else:
        assert  False,"Langayge not be changed"
    roku_ctl.ir_enter('English', roku_ctl.get_launcher_element('RadioButtonItem'))
    for i in range(30):
        xml_info = roku_ctl._get_screen_xml()
        if english_language_tag in xml_info:
            break
        time.sleep(10)
    else:
        assert False,"Langayge not be changed"

