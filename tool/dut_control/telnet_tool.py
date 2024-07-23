# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : telnet_tool.py
# @Time       : 2024/6/11 16:51
# @Author     : chao.li
# @Software   : PyCharm
"""

import logging
import re
import telnetlib
import time
from threading import Thread

from tool.dut_control.executer import Executer

cmd_line_wildcard = {
	'sandia': b'sandia:/ #',
	'sandia_latam': b'sandia_isdb:/ #',
	'sandia_hkc': b'sandia manu:/ #',
	'sandia_dvb': b'sandia_dvb:/ #'
}


class TelnetTool(Executer):
	def __init__(self, ip, wildcard):
		super().__init__()
		self.ip = ip
		self.wildcard = cmd_line_wildcard[wildcard] if type(wildcard) == str else wildcard
		try:
			logging.info(f'Try to connect {ip}')
			self.tn = telnetlib.Telnet()
			self.tn.open(self.ip, port=23)
			self.tn.read_until(self.wildcard).decode('utf-8')
			logging.info('telnet init done')
		# print('telnet init done')
		except Exception as f:
			logging.info(f)

	def execute_cmd(self, cmd):
		self.tn.write(cmd.encode('ascii') + b'\n')
		time.sleep(1)

	def checkoutput(self, cmd, wildcard=''):
		# def run_iperf():
		#     self.tn.write(cmd.encode('ascii') + b'\n')
		#     res = self.tn.read_until(b'Server listening on 5201 (test #2)').decode('gbk')
		#     with open('temp.txt', 'a') as f:
		#         f.write(res)
		if not wildcard:
			wildcard = self.wildcard
		logging.info(f'telnet type cmd : {cmd}')
		self.tn.read_eager()
		self.tn.write(cmd.encode('ascii') + b'\n')
		try:
			res = self.tn.read_very_eager().decode('utf-8').replace('\r\n', '\n')
		except Exception as e:
			self.tn.open(self.ip)
			res = self.tn.read_very_eager().decode('utf-8').replace('\r\n', '\n')
		time.sleep(1)
		return res.strip()

	# def subprocess_run(self, cmd):
	# 	return self.checkoutput(cmd)

	def root(self):
		...

	def remount(self):
		...

	def getprop(self, key):
		return self.checkoutput('getprop %s' % key)

	def get_mcs_tx(self):
		return 'mcs_tx'

	def get_mcs_rx(self):
		return 'mcs_rx'

# tl = TelnetTool('192.168.50.109', 'sandia')
# info = tl.execute_cmd('cat /sys/module/aml_media/parameters/new_frame_count')
# print(tl.tn.read_very_lazy())
# while True:
# 	info = tl.tn.read_very_eager()
# 	if info != b'':
# 		print(info)
# # info = tl.checkoutput('telnet 192.168.50.109 8080', wildcard=b'onn. Roku TV')
# info = tl.checkoutput('dmesg')
# print(info)
# print(info)
# info = tl.checkoutput('logcast start', wildcard=b'Start logcasting')
# print(info)
# time.sleep(2)
# tl.execute_cmd('\x03')  # ,wildcard=b'Console')
# time.sleep(2)
# tl.execute_cmd('\x1A')
# time.sleep(2)
# tl.execute_cmd('telnet 192.168.50.109 8070')
# while True:
# 	info = tl.tn.read_very_eager()
# 	if info != b'':
# 		print(info)
# 		with open('kernel.log', 'a') as f:
# 			f.write(info.decode('utf-8').strip())

# tl.tn.close()
# print(tl.checkoutput('iw wlan0 link'))
# print('aaa')
# print(tl.checkoutput('ls'))
