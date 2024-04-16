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

import pytest
import requests
from roku import Roku

from dut_control.ir import Ir
from tool.dut_control.serial_ctrl import SerialCtrl
from tool.yaml_tool import YamlTool
from tool.dut_control.telnet_tool import TelnetTool

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
roku_config = YamlTool(os.getcwd() + '/config/roku/config.yaml')
roku_ip = roku_config.get_note('dut_ip')
roku_ser = roku_config.get_note('dut_serial')

lock = threading.Lock()


def decode_ignore(info):
	info.decode('utf-8', 'backslashreplace_backport') \
		.encode('unicode_escape') \
		.decode('utf-8', errors='ignore') \
		.replace('\\r', '\r') \
		.replace('\\n', '\n') \
		.replace('\\t', '\t')


class RokuCtrl(Roku, Ir):
	# PTC_SIZE = {
	# 	'Auto': 0,
	# 	'Direct': 1,
	# 	'Normal': 2,
	# 	'Stretch': 3,
	# 	'Zoom': 4
	# }
	_instance = None

	def __new__(cls, *args, **kw):
		if cls._instance is None:
			cls._instance = object.__new__(cls, *args, **kw)
		return cls._instance

	def __init__(self):
		super(RokuCtrl, self).__init__(roku_ip)
		self.settings = ['Network', 'Accessibility', 'TV picture settings', 'TV inputs', 'Audio', 'Guest Mode',
		                 'Home screen', 'Payment method', 'Apple AirPlay and HomeKit', 'Legal notices', 'Privacy',
		                 'Help', 'System']
		self.launcher = ['Home', 'Live TV', 'What to Watch', 'Featured Free', 'Sports', 'Search',
		                 'Streaming Store', 'Settings', 'Secret Screens', 'Debu293g']
		self.hdmi_tv_setting = ['Sleep timer', 'Picture settings', 'Sound settings', 'Accessibility', 'Picture off']

		self.source = {
			'HDMI 1': 'hdmi1',
			'HDMI 2': 'hdmi2',
			'HDMI 3': 'hdmi3',
			'AV': 'cvbs',
			'Live TV': 'dtv',
		}
		self.ip = roku_ip
		self.roku = Roku(roku_ip)
		# self.ser = SerialCtrl(roku_ser['path'], roku_ser['baud'])
		self.ptc_size, self.ptc_mode = '', ''
		self.get_kernel_log()
		self.switch_ir('off')

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

	def get_ir_focus(self):
		# http://192.168.0.121:8060/query/focus/secret
		url = f'http://{self.ip}:8060/query/focus/secret'
		r = requests.get(url)
		result = re.findall(r'<text>(.*?)</text>', r.content.decode('utf-8'), re.S)
		if result:
			logging.info(f"Current ir focus {result[0]}")
			return result[0]
		else:
			return ''

	@classmethod
	def switch_ir(self, status):
		ir_command = {
			'on': 'echo 0xD > /sys/class/remote/amremote/protocol',
			'off': 'echo 0x2 > /sys/class/remote/amremote/protocol'
		}
		logging.info(f'Set roku ir {status}')
		pytest.executer.checkoutput(ir_command[status])

	def get_display_size(self, size):
		for _ in range(7):
			if self.get_ir_focus() == size:
				self.ptc_size = size
				self.select(time=1)
				break
			time.sleep(1)
		else:
			logging.warning(f"Can't set display size into {size}")
		logging.info(f'Current size : {size}')

	def get_display_mode(self, mode):
		for _ in range(7):
			if self.get_ir_focus() == mode:
				self.ptc_mode = mode
				self.select(time=1)
				break
			time.sleep(1)
		else:
			logging.warning(f"Can't set display mode into {mode}")
		logging.info(f'Current mode : {mode}')

	def set_picture_mode(self, mode):
		def ui_down(mode):
			while self.ptc_mode != mode:
				self.down(time=1)

		if self.ptc_mode != mode:
			# mode_list = ['EcoSave', 'Normal', 'Vivid', 'Sports', 'Movie']
			# if mode not in mode_list:
			# 	raise IndexError("Doesn't support this mode, pls check again")
			logging.info(f'Try to set picture mode into {mode}')
			self.info()
			if pytest.light_sensor:
				res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
				if not res:
					self.info()
			else:
				time.sleep(3)
			self.down(time=1)
			self.select(time=1)
			self.down(time=1)
			self.select(time=1)
			t = Thread(target=ui_down, args=(mode,))
			t.daemon = True
			t.start()
			self.get_display_mode(mode)
			self.back(time=1)
			self.back(time=1)

	def set_picture_size(self, size):
		def ui_down(size):
			while self.ptc_size != size:
				self.down(time=1)

		if self.ptc_size != size:
			# if size not in self.PTC_SIZE:
			# 	raise IndexError("Doesn't support this mode, pls check again")
			# logging.info(f'Try to set picture size into {size}')
			self.info()
			if pytest.light_sensor:
				res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
				if not res:
					self.info()
			time.sleep(3)
			self.down(time=1)
			self.select(time=1)
			self.down(time=1)
			self.down(time=1)
			self.select(time=1)
			for _ in range(6):
				self.down(time=1)
			self.select(time=1)
			t = Thread(target=ui_down, args=(size,))
			t.daemon = True
			t.start()
			self.get_display_size(size)
			self.back(time=1)
			self.back(time=1)
			self.back(time=1)

	def get_dmesg_log(self):
		with open('dmesg.log','a') as f:
			info = pytest.executer.checkoutput('dmesg')
			f.write(info)
		pytest.executer.checkoutput('dmesg -c')

	def get_kernel_log(self):
		def run_logcast():
			logging.info('start telnet 8080 to caputre kernel log ')
			tl = TelnetTool(self.ip, 'sandia')
			info = tl.checkoutput(f'telnet {self.ip} 8080', wildcard=b'onn. Roku TV')
			# logging.info(info)
			tl.execute_cmd('logcast start')
			time.sleep(2)
			tl.execute_cmd('\x03')  # ,wildcard=b'Console')
			time.sleep(2)
			tl.execute_cmd('\x1A')
			time.sleep(2)
			tl.execute_cmd(f'telnet {self.ip} 8070')
			while True:
				info = tl.tn.read_very_eager()
				if info != b'':
					with open('kernel.log', 'a', encoding='utf-8') as f:
						try:
							info = info.decode('utf-8').strip()
						except Exception as e:
							info = ''
						f.write(info)

		logging.info("Open 8070 to get kernel log")
		t = Thread(target=run_logcast)
		t.daemon = True
		t.start()

	# def home(self, target='Home'):
	#     logging.info('goto home')
	#     self.roku.home()
	#     if target not in self.launcher:
	#         raise ValueError(f"Doesn't support this ui {target}")
	#     self.send('home', 1)
	#     self.send('home', 3)
	#     # pytest.light_sensor.count_kpi(0, roku_lux.get_note('launcher_50_40')[pytest.panel])
	#     for _ in range(self.launcher.index(target)):
	#         self.send('down', 1)

	# def sources(self, target='HDMI 1'):
	#     logging.info(f'goto {target}')
	#     if target not in self.source:
	#         raise IndexError("Not such this source ,pls check again")
	#     self.roku[f"tvinput.{self.source[target]}"].launch()

	def antenna_scan(self, type='Antenna'):
		'''
		launcher -> live tv -> Antenna and input -> Antenna
		:return:
		'''
		logging.info('goto scan')
		self.send('enter', 3)
		antenna_type = ['Antenna', 'Cable', 'Both', 'Do this later']
		self.sources()
		for i in range(antenna_type.index(type)):
			self.send('down', 1)
		self.send('enter', 1)

	def antenna_rescan(self):
		self.sources()
		self.send('setting', 1)
		self.send('enter')

	def enter_antenna(self):
		self.sources()
		self.send('back', 1)

	def enter_settings(self, setting):
		logging.info(f'goto {setting}')
		if setting not in self.settings:
			raise ValueError(f"Doesn't support this setting {setting}")
		self.home('Settings', 1)
		self.send('enter', 1)
		# pytest.light_sensor.count_kpi(2, {'do': 0, 'ao': [0, 450]}, hold_times=10)
		for _ in range(self.settings.index(setting)):
			self.send('down', 1)

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

# def wakeup(self):
#     count = 0
#     while not pytest.light_sensor.check_backlight():
#         # wake upthe dut before test
#         self.send('power')
#         time.sleep(10)
#         if count > 5:
#             raise EnvironmentError("Pls check ir control")
