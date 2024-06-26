# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 15:09
# @Author  : chao.li
# @File    : rokuIr.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import os
import re
import threading
import time
from threading import Thread
from urllib.parse import quote_plus, urlparse
from xml.etree import ElementTree as ET

import pytest
import requests
from roku import Roku

from dut_control.ir import Ir
from tool.dut_control.serial_ctrl import SerialCtrl
from tool.dut_control.telnet_tool import TelnetTool
from tool.yaml_tool import YamlTool

COMMANDS = {
	# Standard Keys
	"home": "Home",
	"reverse": "Rev",
	"forward": "Fwd",
	"play": "Play",
	"select": "Select",
	"left": "Left",
	"right": "Right",
	"down": "Down",
	"up": "Up",
	"back": "Back",
	"replay": "InstantReplay",
	"info": "Info",
	"backspace": "Backspace",
	"search": "Search",
	"enter": "Enter",
	"literal": "Lit",
	# For devices that support "Find Remote"
	"find_remote": "FindRemote",
	# For Roku TV
	"volume_down": "VolumeDown",
	"volume_up": "VolumeUp",
	"volume_mute": "VolumeMute",
	# For Roku TV while on TV tuner channel
	"channel_up": "ChannelUp",
	"channel_down": "ChannelDown",
	# For Roku TV current input
	"input_tuner": "InputTuner",
	"input_hdmi1": "InputHDMI1",
	"input_hdmi2": "InputHDMI2",
	"input_hdmi3": "InputHDMI3",
	"input_hdmi4": "InputHDMI4",
	"input_av1": "InputAV1",
	# For devices that support being turned on/off
	"power": "Power",
	"poweroff": "PowerOff",
	"poweron": "PowerOn",
}

SENSORS = ("acceleration", "magnetic", "orientation", "rotation")

roku_lux = YamlTool(os.getcwd() + '/config/roku/roku_changhong.yaml')
roku_config = YamlTool(os.getcwd() + '/config/config.yaml')
roku_ip = roku_config.get_note("connect_type")['telnet']['ip']
# roku_ser = roku_config.get_note('dut_serial')

lock = threading.Lock()


def decode_ignore(info):
	info.decode('utf-8', 'backslashreplace_backport') \
		.encode('unicode_escape') \
		.decode('utf-8', errors='ignore') \
		.replace('\\r', '\r') \
		.replace('\\n', '\n') \
		.replace('\\t', '\t')


class RokuCtrl(Roku, Ir):
	_instance = None
	VIDEO_STATUS_TAG = [
		r'screen size \d+x\d+',  # pal层设置video参数时会调用到set property,给vsink设置下来，包括是否是2k/screen size等
		# r'set source window rect',  # 设置视频窗口的位置和宽高
		# r'v4l_get_capture_port_formats: Found \d+ capture formats',  # 获得解码器可支持的codec类型
		# r'avsync session \d+',  # pal层设置video参数时会调用到set property，给asink设置下来，包括是否等待video以及等待时间等
		r'ready to paused',  # 切换状态为pause
		r'output port requires \d+ buffers',  # 申请outputbuffer用于存放es数据
		r'starting video thread',  # video第一帧送入，开始解码线程
		r'detected audio sink GstAmlHalAsink',  # 检测是否有audio element
		r'handle_v4l_event: event.type:\d+, event.u.src_change.changes:\d+',
		# 收到decoder发送的解出第一笔,resolution change 的signal
		r'v4l_setup_capture_port: capture port requires \d+ buffers',  # 申请buffer用于存放解码后的yuv数据
		r'video_decode_thread:<video_sink> emit first frame signal ts \d+',  # decoder解出第一帧，向pal层发送first frame的signal
		r'display_engine_show: push frame: \d+',  # push_frame就是decoder解出的yuv数据
		# r'gst_aml_hal_asink_pad_event:<audio_sink> done',  # audio 数据流开始start
		# r'gst_aml_vsink_change_state:<video_sink> paused to playing avsync_paused \d+',
		# rokuo收到video start,就会下发setspeed1，pipeline状态切换为playing，正式起播
		# r'gst_aml_hal_asink_change_state:<audio_sink> paused to playing',
		r'display_thread_func: pop frame: \d+',
		r'gst_aml_hal_asink_event:<audio_sink> receive eos',
		r'video_eos_thread:<video_sink> Posting EOS',
		r'gst_aml_hal_asink_change_state:<audio_sink> ready to null',
		r'gst_aml_vsink_change_state:<video_sink> ready to null'
	]

	AML_SINK_ERROR_TAG = re.compile(r'gst_caps_new_empty failed|gst_pad_template_new failed|'
	                                r'dec ope fail|can not get formats|can not build caps|invalid dw mode \d+|'
	                                r'Bad screen properties string|Bad source window properties string|'
	                                r'Bad window properties string|not accepting format\(\w+\)|'
	                                r'no memory for codec data size \d+|gst_buffer_map failed for codec data|'
	                                r'fail to create thread|V4L2_DEC_CMD_STOP output fail \d+|'
	                                r'postErrorMessage: code \d+ \(\w+\)|meta data is invalid|'
	                                r'Get mate head error|Metadata oversize \d+ > \d+, please check|'
	                                r'VIDIOC_G_FMT error \d+|cap VIDIOC_STREAMOFF error \d+|'
	                                r'v4l_dec_config failed|fail to get visible dimension \d+|'
	                                r'fail to get cropcap \d+|setup capture fail|streamon failed for output: rc \d+ errno \d+|'
	                                r'fail VIDIOC_DQEVENT \d+|VIDIOC_G_PARM error \d+ rc \d+|'
	                                r'cap VIDIOC_DQBUF fail \d+|start avsync error|VIDIOC_STREAMOFF fail ret:\d+|'
	                                r'set secure mode fail|v4l_dec_dw_config failed|set output format \w+ fail|'
	                                r'setup output fail|can not get output buffer \d+|queuing output buffer failed: rc \d+ errno \d+|'
	                                r'start_video_thread failed|dec open fail|uvm open fail|get capture format fail|'
	                                r'reg event fail|start render fail|invalid para \d+ \d+|free index \d+ fail|'
	                                r'queue cb fail \d+|unable to open file \w+|unable to get pts from: \w+|'
	                                r'fail to open \w+|fail to write \w+ to \w+|set volume fail \d+|stream mute fail:\d+|'
	                                r'invalid sync mode \d+|invalid value:\w+|can not get string|wrong ac4_lang:\w+|'
	                                r'wrong ac4_lang2:\w+|wrong ass type \w+|rate \d+.?\d+ fail|no stream opened|'
	                                r'create av sync fail|segment event not received yet|create timer fail|create thread fail|'
	                                r'out buffer fail \d+|wrong size \d+/\d+|asink open failure|fail to load hw:\d+|'
	                                r'OOM|unsupported channel number:\d+|invalid port:\d+|can not open output stream:\d+|'
	                                r'pause failure:\d+|parse ac4 fail|frame too big \d+|header too big \d+|'
	                                r'trans mode write fail \d+/\d+|drop data \d+/\d+|null pointer')

	def __new__(cls, *args, **kw):
		if cls._instance is None:
			cls._instance = object.__new__(cls, *args, **kw)
		return cls._instance

	def __init__(self):
		super(RokuCtrl, self).__init__(roku_ip)
		self.ip = roku_ip
		self.ptc_size, self.ptc_mode = '', ''
		self.get_kernel_log()
		self.switch_ir('off')
		self.current_target_array = 'launcher'
		self._layout_init()
		# 用于记录当前 遥控光标所在 控件名称
		self.ir_current_location = ''
		logging.info('roku init done')

	def _layout_init(self):
		'''
		存放ui 布局相关位置信息
		形式为二维数组 行列对应ui 控件行列 原点左上角
		Returns:

		'''
		self.media_player_home = [['All', 'Video', 'Audio', 'Photo']]
		self.media_player_help_setting = [['Help'], ['Request media type at startup - [On]'],
		                                  ['Lookup album art on Web - [On]'], ['Display format - [Grid]'],
		                                  ['Autorun - [On]'], ['OK']]

	def __getattr__(self, name):
		if name not in COMMANDS and name not in SENSORS:
			raise AttributeError(f"{name} is not a valid method")

		def command(*args, **kwargs):
			if name in SENSORS:
				keys = [f"{name}.{axis}" for axis in ("x", "y", "z")]
				params = dict(zip(keys, args))
				self.input(params)
			elif name == "literal":
				for char in args[0]:
					path = f"/keypress/{COMMANDS[name]}_{quote_plus(char)}"
					self._post(path)
			elif name == "search":
				path = "/search/browse"
				params = {k.replace("_", "-"): v for k, v in kwargs.items()}
				self._post(path, params=params)
			else:
				if len(args) > 0 and (args[0] == "keydown" or args[0] == "keyup"):
					path = f"/{args[0]}/{COMMANDS[name]}"
				else:
					path = f"/keypress/{COMMANDS[name]}"
				self._post(path)
			if 'time' in kwargs.keys():
				time.sleep(kwargs['time'])

		return command

	def capture_screen(self, filename):
		logging.info("\rStart to capture screen ....\r")
		para = {'param-image-type': 'jpeg'}
		url = "http://%s:8060/capture-screen/secret" % (roku_ip)
		r = requests.get(url, json=para)
		response = r.content

		with open(file=filename, mode='wb') as handle:
			handle.write(response)
			handle.close()

	def load_array(self, array_txt):
		'''
		从 layout/xxx.txt 中 解析出二维数组
		Args:
			array_txt:

		Returns:

		'''
		with open(os.getcwd() + f'/config/roku/layout/{array_txt}') as f:
			info = f.readlines()
			arr = [i.strip().split(',') for i in info]
		return arr

	def get_ir_focus(self, filename='dumpsys.xml'):
		'''
		从roku 服务器获取当天tv 页面的空间xml
		解析xml 获取 focused="true"
		返回解析 得到的 列表中 最后一个元素
		Returns:

		'''
		# http://192.168.0.121:8060/query/focus/secret
		# url = f'http://{self.ip}:8060/query/focus/secret'
		# r = requests.get(url)
		# result = re.findall(r'<text>(.*?)</text>', r.content.decode('utf-8'), re.S)
		# if result:
		# 	logging.info(f"Current ir focus {result[0]}")
		# 	return result[0]
		# else:
		# 	return ''

		self._get_screen_xml(filename)
		tree = ET.parse(filename)
		root = tree.getroot()

		node_list = []
		for child in root:
			for child_1 in child.iter():
				if child_1.tag == 'ItemDetailsView':
					for child_2 in child_1.iter():
						if child_2.tag == 'Label' and child_2.attrib['name'] == 'title':
							# logging.info(child_2.attrib['text'])
							if child_2.attrib['text']:
								if '|' in child_2.attrib['text']:
									# 处理 media player audio ui 多文件名描述
									self.ir_current_location = child_2.attrib['text'].split('|')[0].strip()
								else:
									self.ir_current_location = child_2.attrib['text']
								return self.ir_current_location
				if child_1.tag == 'RenderableNode' and child_1.attrib.get('focused') and child_1.attrib[
					'focused'] == 'true':
					# 处理 picture mode 相关 悬浮菜单
					if child_1.attrib.get('uiElementId') and child_1.attrib['uiElementId'] != 'overlay-root':
						self.ir_current_location = \
							child_1.find('RadioButtonItem').find('ScrollingLabel').find('Label').attrib['text']
						# logging.info(f'{self.ir_current_location}')
						return self.ir_current_location
				if child_1.tag == 'Button' and child_1.attrib.get('focused') and child_1.attrib['focused'] == 'true':
					self.ir_current_location = child_1.find('Label').attrib['text']
					# logging.info(f'show display {self.ir_current_location}')
					return self.ir_current_location
				if child_1.tag == 'StandardGridItemComponent':
					if child_1.attrib.get('focused') and child_1.attrib['focused'] == 'true':
						# logging.info(child_1.attrib['text'])
						node_list.append(child_1)
		if node_list:
			self.ir_current_location = node_list[-1].find('LayoutGroup').find('Label').attrib['text']

	def get_ir_index(self, name, array):
		'''

		Args:
			name: 需要查询的目标 名字
			array: 需要查询的 二维数组

		Returns:

		'''
		if type(array) == str:
			target_array = self.load_array(self.current_target_array + '.txt')
		else:
			target_array = array
		# logging.info(f"Try to get index of  {name}")
		# logging.info(f'Target array {array}')
		for i in target_array:
			for y in i:
				if name == y:
					# logging.info(f'Get location : {target_array.index(i)}  {i.index(y)}')
					return (target_array.index(i), i.index(y))
		logging.warning("Can't find such this widget")
		return None

	def ir_navigation(self, target, array):
		self.get_ir_focus()
		# logging.info(f'ir_navigation {array}')
		logging.info(f'{self.ir_current_location} {target}')
		current_index = self.get_ir_index(self.ir_current_location, array)
		target_index = self.get_ir_index(target, array)
		x_step = abs(target_index[0] - current_index[0])
		y_step = abs(target_index[1] - current_index[1])
		if x_step == 0 and y_step == 0:
			logging.info('navigation done')
			return True
		if target_index[0] > current_index[0]:
			self.down(time=1)
		elif target_index[0] == current_index[0]:
			if target_index[1] > current_index[1]:
				self.right(time=1)
			else:
				self.left(time=1)
		else:
			self.up(time=1)
		return self.ir_navigation(target, array)

	def ir_enter(self, target, array):
		self.ir_navigation(target, array)
		self.select(time=0.5)

	def _get_screen_xml(self, filename='dumpsys.xml'):
		'''
		http://192.168.50.109:8060/query/screen/secret
		从roku 服务器获取当前页面的 控件xml
		Returns:

		'''
		r = ''
		for _ in range(5):
			url = f"http://{roku_ip}:8060/query/screen/secret"
			r = requests.get(url).content.decode('utf-8')
			if 'Internal error' not in r:
				break
		with open(file='dumpsys.xml', mode='w', encoding='utf-8') as handle:
			handle.write(r)
		return r

	def get_u_disk_file_distribution(self, filename='dumpsys.xml'):
		'''
		解析xml 获取u 盘内 folder 分布 以及 file 分布
		Returns: 二维数组

		'''
		self._get_screen_xml(filename)
		tree = ET.parse(filename)
		root = tree.getroot()

		node_list, temp = [], []
		current_file = ''
		for child in root:
			for child_1 in child.iter():
				# 解析StandardGridItemComponent element
				if child_1.tag == 'StandardGridItemComponent':
					index = int(child_1.attrib['index'])
					for child_2 in child_1.iter():
						# if child_2.tag == 'Poster' and 'poster_' in child_2.attrib['uri']:
						# 	type = re.findall(r'poster_(.*?)_fhd', child_2.attrib['uri'])[0]
						if child_2.tag == 'Label' and child_2.attrib['name'] == 'line1':
							if index == 0:
								if temp:
									node_list.append(temp)
								temp = []
							temp.append(child_2.attrib['text'])
		self.media_player_dumpsys = node_list
		return node_list

	@classmethod
	def switch_ir(self, status):
		ir_command = {
			'on': 'echo 0xD > /sys/class/remote/amremote/protocol',
			'off': 'echo 0x2 > /sys/class/remote/amremote/protocol'
		}
		logging.info(f'Set roku ir {status}')
		pytest.executer.checkoutput(ir_command[status])

	def get_display_size(self, size):
		for _ in range(9):
			if self.get_ir_focus() == size:
				self.ptc_size = size
				self.select(time=1)
				break
			self.down(time=1)
			time.sleep(1)
		else:
			logging.warning(f"Can't set display size into {size}")
		logging.info(f'Current size : {size}')

	def get_display_mode(self, mode):
		for _ in range(9):
			if self.get_ir_focus() == mode:
				self.ptc_mode = mode
				self.select(time=1)
				break
			self.down(time=1)
			time.sleep(1)
		else:
			logging.warning(f"Can't set display mode into {mode}")
		logging.info(f'Current mode : {mode}')

	def set_picture_mode(self, mode):

		self.info(time=3)
		if pytest.light_sensor:
			res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
			if not res:
				self.info()
		self.down(time=1)
		self.select(time=1)
		self.down(time=1)
		for i in mode:
			logging.info(f'Try to set picture mode into {i}')
			self.select(time=1)
			if self.ptc_mode != i:
				self.get_display_mode(i)
		self.back(time=1)
		self.back(time=1)

	def set_picture_size(self, size):
		self.info(time=3)
		if pytest.light_sensor:
			res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
			if not res:
				self.info()
		self.down(time=1)
		self.select(time=1)
		self.down(time=1)
		self.down(time=1)
		self.select(time=1)
		for _ in range(6):
			self.down(time=1)
		for i in size:
			logging.info(f'Try to set picture size into {i}')
			self.select(time=1)
			if self.ptc_size != i:
				self.get_display_size(i)
		self.back(time=1)
		self.back(time=1)
		self.back(time=1)

	def get_dmesg_log(self):
		with open('dmesg.log', 'a') as f:
			info = pytest.executer.checkoutput('dmesg')
			f.write(info)
		pytest.executer.checkoutput('dmesg -c')

	def get_kernel_log(self, filename='kernel.log'):

		def run_logcast(filename):
			while True:
				info = tl.tn.read_very_eager()
				if info != b'':
					with open(filename, 'a', encoding='utf-8') as f:
						try:
							info = info.decode('utf-8').replace('\r\n', "\n")
						except Exception as e:
							info = ''
						f.write(info)

		logging.info('start telnet 8080 to caputre kernel log ')
		tl = TelnetTool(self.ip, 'sandia')
		info = tl.checkoutput(f'telnet {self.ip} 8080', wildcard=b'onn. Roku TV')
		# logging.info(info)
		tl.execute_cmd('logcast start')
		time.sleep(1)
		tl.execute_cmd('\x03')  # ,wildcard=b'Console')
		time.sleep(1)
		tl.execute_cmd('\x1A')
		time.sleep(1)
		tl.execute_cmd(f'telnet {self.ip} 8070')
		t = Thread(target=run_logcast, args=(filename,))
		t.daemon = True
		t.start()

	def analyze_logcat(self, re_list, timeout=60):
		'''
		dut 需配置 autostart 文件
		push autostart 文件
		1. 创建文件加mkdir -p /nvram/debug_over/etc
		2. cp /etc/autostart /nvram/debug_overlay/etc
		3. vi /nvram/debug_overlay/etc/autostart
		4. export GST_DEBUG=2,amlvsink:6,amlhalasink:6
		5. 重启 dut
		Args:
			re_list:

		Returns:

		'''
		tl = TelnetTool(self.ip, pytest.executer.wildcard)
		tl.checkoutput('logcat')
		start = time.time()
		while re_list and (time.time() - start < timeout):
			info = tl.tn.read_very_eager()
			if info != b'':
				info = info.decode('utf-8').replace('\r\n', "\n")
				with open('logcat.log', 'a') as f:
					f.write(info)
				for i in info.split('\n'):
					# logging.info(f'info : {info}')
					if len(re_list) >= 5 and (time.time() - start > 5):
						logging.warning('Playback init with error')
						pytest.executer.checkoutput('\x03')
						return False
					if re_list and re.findall(re_list[0], i):
						logging.info(re_list[0])
						re_list.pop(0)

		pytest.executer.checkoutput('\x03')

	def catch_err(self, filename, tag_list):
		'''

		Args:
			filename:  需要检测的log文件
			tag_list: 需要捕捉的 关键字 正则表达是

		检测到正则时会通过 logging 输出
		Returns:

		'''
		logging.info(f'Start to catch err. Logfile :{filename}')
		with open(filename, 'r') as f:
			info = f.readlines()
		for i in info:
			res = tag_list.findall(i)
			if res:
				logging.warning(res)
		logging.info('Catch done')

	def shutdown(self):
		count = 0
		while pytest.light_sensor.check_backlight():
			# shut down the dut before test
			self.send('power', 10)
			if count > 5:
				raise EnvironmentError("Pls check ir control")

	def get_hdmirx_info(self, **kwargs):
		logging.info(f'hdmirx for expect : {kwargs}')

		def match(info):
			res = re.findall(
				r'Hactive|Vactive|Color Depth|Frame Rate|TMDS clock|HDR EOTF|Dolby Vision|HDCP Debug Value|HDCP14 state|HDCP22 state|Color Space',
				info)
			if res:
				return res

		for _ in range(3):
			try:
				info = pytest.executer.checkoutput('cat /sys/class/hdmirx/hdmirx0/info')
			# info = pytest.executer.checkoutput('dmesg')
			# pytest.executer.checkoutput('dmesg -c')
			except Exception:
				info = ''
			if 'HDCP1.4 secure' in info:
				break
			time.sleep(2)

		logging.info(info)
		info = [i.strip() for i in info.split('\n') if match(i)]
		logging.info(' ,'.join(info[:5]))
		logging.info(' ,'.join(info[5:]))
		result = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in info}
		for k, v in kwargs.items():
			if k == 'depth':
				k = 'Color Depth'
			if k == 'space':
				k = 'Color Space'
			if k == 'frame':
				k = 'Frame Rate'
				if int(result[k]) not in range(*v):
					logging.warning(f'{result[k]} not in expect , should in {v}')
					return False
			else:
				if result[k] != v:
					logging.warning(f'{result[k]} not in expect , should be {v}')
					return False
		else:
			return True

	def enter_media_player(self):
		self['2213'].launch()
		count = 0
		while True:
			self.get_ir_focus()
			with open('dumpsys.xml', 'r', encoding='utf-8') as f:
				if 'Media Type Selection' in f.read():
					logging.info('enter done')
					return
				self.back(time=1)
				if count > 5:
					logging.warning("Can't open media player")
				time.sleep(3)

	def check_udisk(self):
		'''
		在media player 界面内 检测是否 外接u盘
		dumpsys 当前页面
		判断是否存在 Connecting to a DLNA Media Server or USB Device 字样
		Returns:

		'''
		return 'Select Media Device' in self._get_screen_xml()
