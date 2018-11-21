# -*- coding:utf-8 -*-

import dataPreprocess.xls2lua
import datetime

# 通过导表程序获得所有字典形式的数据，用于后面的抽取，开宝箱，关卡统计等各种计算的数据池

allExcelDictData = dataPreprocess.xls2lua.getAllExcelDictData(dataPreprocess.getFilePath.getFilePath())
# allExcelDictData = dataPreprocess.xls2lua.getAllExcelDictData()

if __name__ == "__main__":
    start = datetime.datetime.now()
    # print("vvvvv", allExcelDictData)
    # print("vvvvv", allExcelData)
    allExcelDictData()
    # print(get1Data(getAllExcelDictData()))
    print(dataPreprocess.xls2lua.getAllExcelDictData(dataPreprocess.getFilePath.getFilePath()))
    end = datetime.datetime.now()

    print("执行计算共用了 ",end-start," 秒！")

