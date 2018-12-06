# -*- coding:utf-8 -*-

import xlwt

class createExcel():
    """创建excel对象，并实现以下功能：
    1. 检查result.xls是否已经存在
    2. 向excel中填写数据，按照类型，和副本ID，或者章节来创建名称然后写入数据
    """
    def __init__(self, excelName):
        self.excelName = excelName


