# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/27 15:06
# @Author  : chao.li
# @File    : pil_tool.py
# @Project : kpi_test
# @Software: PyCharm


from PIL import Image, ImageChops


class PilTool:

    def __init__(self):
        ...

    def compare_images(self, path_one, path_two, diff_save_location):
        """
        比较图片，如果有不同则生成展示不同的图片

        @参数一: path_one: 第一张图片的路径
        @参数二: path_two: 第二张图片的路径
        @参数三: diff_save_location: 不同图的保存路径
        """
        image_one = Image.open(path_one)
        image_two = Image.open(path_two)
        try:
            diff = ImageChops.difference(image_one, image_two)

            if diff.getbbox() is None:
                # 图片间没有任何不同则直接退出
                print("【+】We are the same!")
            else:
                diff.save(diff_save_location)
        except ValueError as e:
            text = ("表示图片大小和box对应的宽度不一致，参考API说明：Pastes another image into this image."
                    "The box argument is either a 2-tuple giving the upper left corner, a 4-tuple defining the left, upper, "
                    "right, and lower pixel coordinate, or None (same as (0, 0)). If a 4-tuple is given, the size of the pasted "
                    "image must match the size of the region.使用2纬的box避免上述问题")
            print("【{0}】{1}".format(e, text))
