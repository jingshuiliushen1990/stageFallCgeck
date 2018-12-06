#-*- coding:utf-8 -*-

"""
记录检查过程中使用到的通用接口，防止重复编写，形成代码垃圾
"""

from copy import deepcopy

# 处理得到的数据，生成ID：{对应ID装备的其他数据}的形式，便于后期进行查询处理，节省时间
def initEquipData(allData):
    equipData = allData.get("装备", None)
    undefineEquipData = allData.get("未鉴定装备", None)
    symbolData = allData.get("材料", None)
    tempEquipData = equipData + undefineEquipData + symbolData
    newTempEquipData = deepcopy(tempEquipData)
    newEquipData = {}
    for iEquipData in newTempEquipData:
        newKey = iEquipData.get("id", None)
        type = iEquipData.get("type", None)
        if newKey and (type in [20, 25, 2]):
            iEquipData.pop("id", "no_key")
            newEquipData[newKey] = iEquipData
        else:
            continue
    return newEquipData

# # 获得徽记数据
# def getSymbolData(allData):
#     materialsData = allData.get("材料", None)
#     symbolData = []
#     for i in materialsData:
#         if i["type"] == 25:
#             symbolData.append(i)
#         else:
#             continue
#     return symbolData


if __name__ == "__main__":
    from getConfigData.loadAllDictData import *
    ifilePath = "E:\\M1_SVN\\Market_build\\lss\\config\\resource\\"
    data = getLocalConfigData(ifilePath)
    # initEquipData(data)
    print("***********", initEquipData(data))