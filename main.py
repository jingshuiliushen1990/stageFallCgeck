#-*- coding:utf-8 -*-

from rwFile.getExcelData import *

excelObj = getExcelData("config.xlsx")
constData = excelObj.getSheetData("常量配置")
print("EEEEE", constData)

if (constData and constData["isUseLocalData"]):
    pass

