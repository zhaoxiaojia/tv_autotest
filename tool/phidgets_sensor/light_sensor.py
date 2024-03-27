# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : light_sensor.py
# @Time       : 2024/3/12 10:59
# @Author     : chao.li
# @Software   : PyCharm
"""
import logging
import time

from Phidget22.Devices.LightSensor import *
from Phidget22.Phidget import *

illuminance_value = 0


def onIlluminanceChange(self, illuminance):
	global illuminance_value
	illuminance_value = int(illuminance)


class lightSensor():
	def __init__(self):
		self.light_sensor = LightSensor()
		self.light_sensor.setOnIlluminanceChangeHandler(onIlluminanceChange)
		self.light_sensor.openWaitForAttachment(3000)

	def count_kpi(self, sensor, target=[], inflection_point=[], time_out=10):
		if type(target) == int:
			target = range(target - 5, target + 5)
		elif type(target) == list:
			target = range(*target)
		if type(inflection_point) == int:
			inflection_point = [inflection_point, ]
		logging.info(f'Illumiance should in {target}')
		logging.info('Catch illumiance')
		count_temp = 0
		start = time.time()
		inflection_flag = False
		temp = 0
		while time.time() - start < time_out:
			temp += 1
			if inflection_point and not inflection_flag:
				logging.info(inflection_point)
				for i in inflection_point:
					if type(i) == int:
						inflection_target = [i for i in range(i - 5, i + 5)]
					elif type(i) == list:
						inflection_target = [j for j in range(*i)]
					else:
						raise ValueError("Doesn't support this type")
					while not illuminance_value in inflection_target:
						time.sleep(0.01)
						if time.time() - start > time_out:
							return 0
						continue
			else:
				time.sleep(0.01)
			# if temp % 5 == 0:
			# 	print('Illumiance: ' + str(illuminance_value))
			if illuminance_value in target:
				logging.info(f'Illumiance in expect :  {illuminance_value}')
				return 1
		else:
			logging.info(f'Current illumiance : {illuminance_value}')
			logging.warning("Can't catch the targe data")
			return 0

# def __del__(self):
# 	if hasattr(self,'light_sensor') and isinstance(self.light_sensor,LightSensor):
# 		self.light_sensor.close()
