#-*- coding:utf-8 -*-

"""
记录检查过程中使用到的通用接口，防止重复编写，形成代码垃圾
"""

from getConfigData.loadAllDictData import *
import time

# 处理得到的数据，生成ID：{对应ID装备的其他数据}的形式，便于后期进行查询处理，节省时间
def initEquipData(allData):
    equipData = allData.get("装备", None)
    undefineEquipData = allData.get("未鉴定装备", None)
    equipData.extend(undefineEquipData)
    newEquipData = {}
    for iEquipData in equipData:
        newKey = iEquipData["id"]
        del iEquipData["id"]
        newEquipData[newKey] = iEquipData

    return newEquipData




if __name__ == "__main__":
    ifilePath = "E:\\M1_SVN\\Market_build\\lss\\config\\resource\\"
    data = getLocalConfigData(ifilePath)
    print("***********", initEquipData(data))