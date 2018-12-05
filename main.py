#-*- coding:utf-8 -*-

from rwFile.getExcelData import *
from checkCode.equipStageCheck import *
import threading

excelObj = getExcelData("config.xlsx")
constData = excelObj.getSheetData("常量配置")
print("%%%%%%%", constData)





