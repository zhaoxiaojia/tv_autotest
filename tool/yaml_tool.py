#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

@File		:	yaml_tool.py
@Time		:	2023-12-11 19:47:01
@Author		:	chao.li
@Desc		:	None


'''

import yaml

'''
yaml 格式现在校验网站
https://www.bejson.com/validators/yaml_editor/
'''


class YamlTool:
    def __init__(self, path):
        self.path = path
        with open(path,encoding='utf-8') as a_yaml_file:
            # 解析yaml
            self.parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

    def get_note(self, note):
        return self.parsed_yaml_file.get(note)


# yaml_config = yamlTool("/Users/chao.li/kpi_test/config/config.yaml")
