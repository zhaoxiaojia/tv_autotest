# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:50
# @Author  : chao.li
# @File    : coco.py
# @Project : kpi_test
# @Software: PyCharm
import re
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

from xml.etree import ElementTree as ET
import requests

url = f"http://192.168.50.109:8060/query/screen/secret"
r = requests.get(url).content.decode('utf-8')

with open(file='dumpsys.xml', mode='w') as handle:
	handle.write(r)

tree = ET.parse('dumpsys.xml')
root = tree.getroot()

node_list, temp = [], []

for child in root:
	for child_1 in child.iter():
		# 解析StandardGridItemComponent element
		if child_1.tag == 'StandardGridItemComponent':
			index = int(child_1.attrib['index'])
			for child_2 in child_1.iter():
				if child_2.tag == 'Poster':
					type = re.findall(r'poster_(.*?)_fhd', child_2.attrib['uri'])[0]
				if child_2.tag == 'Label' and child_2.attrib['name'] == 'line1':
					if index == 0:
						if temp:
							node_list.append(temp)
						temp = []
					temp.append(child_2.attrib['text'])
			print('line 53 node_list', node_list)
			print('-' * 40)

print(node_list)

map = [['coco', 'zues', 'lichao', 'USB-photo', 'USB-video-audio'], ['auto_roku_usb'],
       ['1080p24-H264-AAC_Trailer_Inception Trailer 2', 'A - Pufferfish', 'aac', 'bbb-4mbps-24fps.h264.ac3',
        'Big_Buck_Bunny_MKV_Multi_Subs_30_FPS'], ['Dex3cc', 'DTS', 'h262_mp2', 'h264_aac_Subtitles', 'h264_ac3'],
       ['h264_alac', 'h264_dts', 'h264+aac-48000-321-51', 'h264+ac3-48000-200-st', 'h265+ac3-48000-200-st'],
       ['hdr10', 'LG_Chess_HDR', 'LG_Chess_HDR_2K_1920_1080_HDR10', 'MKV_AVC(1920x816)_DTS(6)', 'mkv-h265 - jellyfish'],
       ['MKV-VP9-2K-AAC', 'tears-of-steel-4k-h-265', '003_Roku_Dec._2019_Final_Delivery_HEVC_10bit_100Mbps_Ultra High'],
       ['Kalimba', 'Symphony No. 9 (Scherzo)', 'ac3-48000-200-st', 'Sleep Away', 'dolby digital ac3'],
       ['eac3-48000-200-st', 'flac', 'pcm_s8-48000-201-21', 'pcm_s8-48000-220-quads',
        'Chrono Cross Another Inspiration OC ReMix'], ['pcm_u8', 'sample-256kbps'],
       ['3840x2160', '4K Square Test Card - 2160x2160', 'slide213787', 'Nvidia_Settings', 'leaves'],
       ['8K Square Test Card - 4320x4320', 'Test Card Result - Slightly Scaled', 'Test Card Result - Scaled 50%',
        'Test Card Result - Correct', '4K Test Card - 3840x2160 - original']]
