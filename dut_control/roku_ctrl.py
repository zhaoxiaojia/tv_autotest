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
import time
from threading import Thread
from urllib.parse import quote_plus, urlparse

import pytest
import requests
from roku import Roku

from dut_control.ir import Ir
from tool.dut_control.serial_ctrl import SerialCtrl
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
roku_config = YamlTool(os.getcwd() + '/config/roku/config.yaml')
roku_ip = roku_config.get_note('dut_ip')
roku_ser = roku_config.get_note('dut_serial')


def decode_ignore(info):
	info.decode('utf-8', 'backslashreplace_backport') \
		.encode('unicode_escape') \
		.decode('utf-8', errors='ignore') \
		.replace('\\r', '\r') \
		.replace('\\n', '\n') \
		.replace('\\t', '\t')


class RokuCtrl(Roku, Ir):
	PTC_SIZE = {
		'Auto': 0,
		'Direct': 1,
		'Normal': 2,
		'Stretch': 3,
		'Zoom': 4
	}

	def __init__(self):
		super(RokuCtrl, self).__init__(roku_ip)
		self.ir = pytest.irsend
		self.settings = ['Network', 'Accessibility', 'TV picture settings', 'TV inputs', 'Audio', 'Guest Mode',
		                 'Home screen', 'Payment method', 'Apple AirPlay and HomeKit', 'Legal notices', 'Privacy',
		                 'Help', 'System']
		self.launcher = ['Home', 'Live TV', 'What to Watch', 'Featured Free', 'Sports', 'Search',
		                 'Streaming Store', 'Settings', 'Secret Screens', 'Debug']
		self.source = {
			'HDMI 1': 'hdmi1',
			'HDMI 2': 'hdmi2',
			'HDMI 3': 'hdmi3',
			'AV': 'cvbs',
			'Live TV': 'dtv',
		}
		self.roku = Roku(roku_ip)
		self.ser = SerialCtrl(roku_ser['path'], roku_ser['baud'])
		self.ptc_size, self.ptc_mode = '', ''

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

	def switch_ir(self, status):
		ir_command = {
			'on': 'echo 0xD > /sys/class/remote/amremote/protocol',
			'off': 'echo 0x2 > /sys/class/remote/amremote/protocol'
		}

		self.ser.write(ir_command[status])

	def get_display_size(self, size):
		info = self.ser.recv_until_pattern(b'Aspect ratio changed to ' + bytes(str(size), encoding='utf-8'))
		# info = ''.join([i.decode('utf-8', "ignore") for i in info])
		# temp = re.findall(r'Aspect ratio changed to (\d)', str(info), re.S)[0]
		temp = {v: k for k, v in self.PTC_SIZE.items()}
		logging.info(f'current size : {temp[size]}')
		self.ptc_size = size
		self.ptc_size_name = list(self.PTC_SIZE.keys())[self.ptc_size]
		self.select(time=1)

	def get_display_mode(self, mode):
		info = self.ser.recv_until_pattern(b'Picture mode changed to ' + bytes(mode, encoding='utf-8'))
		# info = ''.join([i.decode('utf-8', "ignore") for i in info])
		# mode = re.findall(r'Picture mode changed to (\w+)', info, re.S)[0]
		logging.info(f'current mode : {mode}')
		self.ptc_mode = mode
		self.select(time=1)

	def set_picture_mode(self, mode):
		def ui_down(mode):
			while self.ptc_mode != mode:
				self.down(time=3)

		if self.ptc_mode != mode:
			mode_list = ['EcoSave', 'Normal', 'Vivid', 'Sports', 'Movie']
			if mode not in mode_list:
				raise IndexError("Doesn't support this mode, pls check again")
			logging.info(f'Try to set picture mode into {mode}')
			self.info()
			res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
			if not res:
				self.info()
			# self.down(time=1)
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
				self.down(time=3)

		if self.ptc_size != size:
			if size not in self.PTC_SIZE:
				raise IndexError("Doesn't support this mode, pls check again")
			logging.info(f'Try to set picture size into {size}')
			self.info()
			res = pytest.light_sensor.count_kpi(0, roku_lux.get_note('setting_white')[pytest.panel])
			if not res:
				self.info()
			# self.down(time=1)
			self.select(time=1)
			self.down(time=1)
			self.down(time=1)
			self.select(time=1)
			for _ in range(6):
				self.down(time=1)
			self.select(time=1)
			t = Thread(target=ui_down, args=(self.PTC_SIZE[size],))
			t.daemon = True
			t.start()
			self.get_display_size(self.PTC_SIZE[size])
			self.back(time=1)
			self.back(time=1)
			self.back(time=1)

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

	def get_hdmirx_info(self):

		def match(info):
			res = re.findall(
				r'Hactive|Vactive|Color Depth|Frame Rate|TMDS clock|HDR EOTF|Dolby Vision|HDCP Debug Value|HDCP14 state|HDCP22 state',
				info)
			if res:
				return res

		self.ser.write('cat /sys/class/hdmirx/hdmirx0/info')
		info = self.ser.recv()
		for _ in range(10):
			try:
				self.ser.write('cat /sys/class/hdmirx/hdmirx0/info')
				info = self.ser.recv()
			except Exception:
				...
			if 'HDCP1.4 secure' in info:
				break
			time.sleep(1)
		info = [i.strip() for i in info.split('\n') if match(i)]
		logging.info(info)
		logging.info(' ,'.join(info[:5]))
		logging.info(' ,'.join(info[5:]))
		return info

# def wakeup(self):
#     count = 0
#     while not pytest.light_sensor.check_backlight():
#         # wake upthe dut before test
#         self.send('power')
#         time.sleep(10)
#         if count > 5:
#             raise EnvironmentError("Pls check ir control")
