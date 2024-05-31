# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:50
# @Author  : chao.li
# @File    : coco.py
# @Project : kpi_test
# @Software: PyCharm
import re
from xml.etree import ElementTree as ET

import requests

# launcher = [
# 	["Home","coco"],
# 	["Live TV"],
# 	["What to Watch"],
# 	["Featured Free"],
# 	["Sports"],
# 	["Search"],
# 	["Streaming Store"],
# 	["Settings"],
# 	["Secret Screens"],
# 	["Debug"],
# ]


info = [['auto_roku_usb', 'coco', 'lichao', 'USB-photo', 'USB-video-audio'], ['zues'], ['003_Roku_Dec._2019_Final_Delivery_HEVC_10bit_100Mbps_Ultra High', '1080p24-H264-AAC_Trailer_Inception Trailer 2', 'A - Pufferfish', 'aac'], ['bbb-4mbps-24fps.h264.ac3', 'Big_Buck_Bunny_MKV_Multi_Subs_30_FPS', 'Dex3cc', 'DTS'], ['h262_mp2', 'h264+aac-48000-321-51', 'h264+ac3-48000-200-st', 'h264_aac_Subtitles'], ['h264_ac3', 'h264_alac', 'h264_dts', 'h265+ac3-48000-200-st'], ['hdr10', 'LG_Chess_HDR', 'LG_Chess_HDR_2K_1920_1080_HDR10', 'mkv-h265 - jellyfish']]
temp = []
for i in info:
	temp.extend(i)

print(temp)