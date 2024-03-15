# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/21 10:52
# @Author  : chao.li
# @File    : master_8100s.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import os
import time

import serial

# from tool.dut_control.serial_crt import serial_crt
from tool.yaml_tool import YamlTool


class Master_8100s:

	def __init__(self):
		self.serial_data = YamlTool(os.getcwd() + '/config/roku/config.yaml').get_note('pattern_generator')[
			'serial_setting']
		self.serialport = serial.Serial(self.serial_data['path'], self.serial_data['baud'])
		self.serialport.bytesize = serial.EIGHTBITS  # number of bits per bytes
		self.serialport.parity = serial.PARITY_NONE  # set parity check: no parity
		self.serialport.stopbits = serial.STOPBITS_ONE  # number of stop bits
		self.serialport.timeout = 1  # non-block read - timeout block read
		self.serialport.xonxoff = False  # disable software flow control
		self.serialport.rtscts = False  # disable hardware (RTS/CTS) flow control
		self.serialport.dsrdtr = False  # disable hardware (DSR/DTR) flow control
		self.serialport.writeTimeout = 2  # timeout for write
		self.serialport.write(b'\x05')

		self.running_mode = ''
		if self.serialport.isOpen():
			self.serialport.flushInput()  # flush input buffer.
			self.serialport.flushOutput()  # flush output buffer.
			self.status = ''
		else:
			print("# Please check serial port - exit program")

	def callback(self, prefix, name, *args):
		method = getattr(self, prefix + name, None)
		if callable(method):
			return method(*args)
		else:
			logging.info(list(filter(lambda x: prefix in x, dir(self))))

	def close(self):
		self.serialport.write(b'\x04')

	def cmd_start(self):
		self.cmd = b'\x02'
		self.serialport.write(self.cmd)

	def cmd_stop(self, delay=2):
		self.serialport.flushInput()  # flush input buffer.
		self.cmd = b"\x03"
		self.serialport.write(self.cmd)
		if self.running_mode == 'tas':
			time.sleep(2)
		else:
			time.sleep(delay)
		read_messages = self.serialport.readline()
		if (b'\x06' in read_messages):
			return True
		return False

	def switch_ctl(self, name, status):
		cmd = {
			'on': b'\x31',
			'off': b'\x30'
		}
		code = {
			'hdcp': b'\x12',
			'cec': b'\x14'
		}
		for i in range(3):
			print(f'{name.title()} status: {status}')
			self.cmd_start()
			self.serialport.write(code[name])
			self.serialport.write(cmd[status])
			result = self.cmd_stop()
			if result:
				return True

	def setTimmingPattern(self, timming, pattern):
		for _i in range(3):
			print(timming, pattern)
			self.cmd_start()
			self.cmd = b"\x09"
			self.serialport.write(self.cmd)
			self.cmd = str(timming)
			self.cmd = self.cmd.zfill(3)
			self.serialport.write(bytearray(self.cmd.encode()))
			self.cmd = str(pattern)
			self.cmd = self.cmd.zfill(3)
			self.serialport.write(bytearray(self.cmd.encode()))
			result = self.cmd_stop(2)
			if result:
				return True
		print("# Ack Messages is not found")
		return False

	def __del__(self):
		if hasattr(self, 'serialport') and isinstance(self.serialport, serial.Serial) and self.serialport.is_open:
			self.serialport.close()

# master = master_8100s()
# master.setTimmingPattern('371','028')
# time.sleep(1)
# master.serialport.write(b'\x04')
# master.serialport.close()
