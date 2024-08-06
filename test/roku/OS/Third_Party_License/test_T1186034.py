# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/26 9:45
# @Author  : chao.li
# @File    : test_T1186034.py



import logging
import re
import time
from test.roku import *
from command import Common
import pytest

'''

Preconditions
    1. This screen can be accessed by highlighting and selecting Roku Home > Settings > System > Third party licenses menu item.
    2. For newer platforms it can be accessed through Home -> Settings -> Legal Notices -> Third party licenses

Setps:
	1. Highlight Roku Home > Settings > System > Third party licenses menu item and review right part of the screen.
	2. Press all IR remote buttons.
	3. Press all panel buttons.
	4. Select Third-party licenses menu item by pressing 'OK' or 'right' remote control button. Menu 'Options' in the right top corner of the screen should remain disabled within Third-party licenses info section.
	5. Scroll down/up the text by using 'down' and 'up' remote control D-pad buttons.
	6. Scroll Down/Up text by using the "Rewind" and "Fast forward" button in Remote.
	7. Note: For 12.5, Third-party licenses menu can be found in Settings --> Legal notices

Expected Result:
	1. Right part of the screen should contain the graphical artifacts. Make sure text is accurate. Verify content and graphics of the tips is accurate and relevant.
	2. Make sure all expected remote control buttons are functional. Continuous scrolling works as expected.
	3. Make sure all expected panel buttons are functional.
	4. TV navigates to 'Third party licenses' screen. Make sure all the information displayed is accurate.
	5. Make sure text scrolled as expected. Continuous scrolling should work without performance hesitation.
	6. Make sure text scrolled as expected. Continuous scrolling should work without performance hesitation.

'''


@pytest.fixture(autouse=True)
def setup_teardown():
    roku_ctl.home(time=2)
    roku_ctl.home(time=1)
    yield
    roku_ctl.home(time=1)
    roku_ctl.home(time=1)
    roku_ctl.get_dmesg_log()


translation_noclose="{1130, 704}"
translation_close="{1148.5, 585}"

def test_license():
    roku_ctl.ir_enter('Settings', roku_ctl.get_launcher_element('LabelListNativeItem'))
    roku_ctl.ir_enter('Legal notices', roku_ctl.get_launcher_element('ArrayGridItem'))
    if roku_ctl.get_launcher_element('SettingsListItem'):
        roku_ctl.ir_enter('Third party licenses', roku_ctl.get_launcher_element('SettingsListItem'))
    if roku_ctl.get_launcher_element('LabelListItem'):
        roku_ctl.ir_enter('Third party licenses', roku_ctl.get_launcher_element('LabelListItem'))
    time.sleep(2)
    roku_ctl.down('keydown')
    xml_info = roku_ctl._get_screen_xml()
    while translation_close not in xml_info and  translation_noclose not in xml_info:
        time.sleep(5)
        xml_info = roku_ctl._get_screen_xml()
    roku_ctl.down('keyup')
    time.sleep(1)
    if 'text="Close"' in xml_info:
        logging.info('found close')
        roku_ctl.down(time=1)
        roku_ctl.select(time=1)
    else:
        roku_ctl.back(time=1)