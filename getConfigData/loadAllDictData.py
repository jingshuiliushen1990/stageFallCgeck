# -*- coding:utf-8 -*-

from getConfigData.xls2lua import *
from getConfigData.getFilePath import *
import datetime

# 通过导表程序获得所有字典形式的数据，用于后面的抽取，开宝箱，关卡统计等各种计算的数据池
# 获取svn中最新数据，然后然后生成数据字典
def getSvnConfigData():
    return getSvnExcelDictData()

# 获得本地的配置数据字典
def getLocalConfigData(iflePath):
    if isRightFilePath(iflePath):
        # print("%%%%%%%%", getLocalExcelDictData(iflePath).get("装备"))
        return getLocalExcelDictData(iflePath)
    else:
        return False


if __name__ == "__main__":
    start = datetime.datetime.now()
    ifilePath = "E:\\M1_SVN\\Market_build\\lss\\config\\resource\\"

    # print("%%%%%%", getSvnConfigData())
    print("$$$$$$", getLocalConfigData(ifilePath))
    end = datetime.datetime.now()

    print("执行计算共用了 ",end-start," 秒！")

