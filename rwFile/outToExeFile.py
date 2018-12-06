# -*- coding:utf-8 -*-

import xlwt


"""
创建excel对象，并实现以下功能：
1. 检查result.xls是否已经存在
2. 向excel中填写数据，按照类型，和副本ID，或者章节来创建名称然后写入数据
"""

def setStyle(name, height, bold = False, colorIndex = 4):
    style = xlwt.XFStyle()
    font = xlwt.Font()

    font.name = name
    font.bold = bold
    font.color_index = colorIndex
    font.height = height
    style.font = font

    return style


def writeToExcel(iData):
    f = xlwt.Workbook()
    pass
