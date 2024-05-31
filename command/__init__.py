# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : __init__.py.py
# @Time       : 2024/5/24 15:50
# @Author     : chao.li
# @Software   : PyCharm
"""


class Common:
	show_video_width = 'cat /sys/class/video/frame_width'
	show_video_height = 'cat /sys/class/video/frame_width'
	show_frame_decoded = 'cat /sys/module/aml_media/parameters/new_frame_count'
	show_windows_location = 'cat /sys/module/aml_media/parameters/new_frame_count'
	show_frame_rate = 'cat /sys/class/video/frame_rate'
