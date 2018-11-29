# -*- coding:utf-8 -*-

from checkCode.baseClass import commonBase
import requests
import json
from checkCode.universalApi import initEquipData


class equipStage(commonBase):
    """用来计算装备秘境中掉落金装的概率"""

    def __init__(self, stageId, count, lv, career, gender, checkType, goldFallRate):
        super(equipStage, self).__init__(lv, career, gender, count, checkType)
        self.stageId = stageId
        self.goldFallRate = goldFallRate

    def getStageId(self):
        return self.stageId

    def setStageId(self, newStageId):
        self.stageId = newStageId

    def getGoldFallRate(self):
        return self.goldFallRate

    def setGoldFallRate(self, newGoldFallRate):
        self.goldFallRate = newGoldFallRate

    def getPostmanKeyDict(self):
        postmanKeyDict = {}
        postmanKeyDict["stage_id"] = self.stageId
        postmanKeyDict["count"] = self.count
        postmanKeyDict["lv"] = self.lv
        postmanKeyDict["career"] = self.career
        postmanKeyDict["gender"] = self.gender

        return postmanKeyDict

    def getPostmanData(self):
        httpAddr = commonBase.getHttpAddr()
        try:
            postmanData = requests.post(httpAddr, self.getPostmanKeyDict())
            return postmanData.text
        except:
            print("服务器连接不上，请检查连接！！！")
            return False

    def getUsefulPostmanData(self):
        postmanData = self.getPostmanData()
        if not postmanData:
            return False
        else:
            return postmanData.get("data")


    # 处理postman 数据，得到便于统计的形式，然后进行统计
    def initPostmanData(self, allData):
        result = {}
        tempData = self.getUsefulPostmanData()
        # print("%%%%%%%%%%", tempData)
        if tempData:
            for i in tempData:
                checkResult = isEquip(allData, i.get("id"))
                if checkResult:
                    tempResult = {}
                    tempResult["name"] = i.get("name")
                    tempResult["amount"] = i.get("amount")
                    tempResult["attribute"] = checkResult
                    result[i.get("id")] = tempResult
                else:
                    continue
            return result
        return False



# 判断给定的物品编号是不是装备，是的话返回该装备的部位，品质，性别，职业，使用等级， 不是时返回False
def isEquip(allData, goodId):
    newEquipData = initEquipData(allData)
    goodIdInfo = newEquipData.get(goodId, None)
    if goodIdInfo:
        result = []
        result.append(goodIdInfo.get("sub_type"))
        result.append(goodIdInfo.get("quality"))
        result.append(goodIdInfo.get("gender"))
        result.append(goodIdInfo.get("careers"))
        result.append(goodIdInfo.get("use_level"))
        result.append(goodIdInfo.get("type"))
        return result
    else:
        return False


# 判断装备等级投放是否合理，当返回 1 时，说明投放与等级相符
# 当返回 2 时，说明投放的是低级装备
# 当返回 3 时，说明投放的装备比玩家的等级高10级，这里有问题
# 掉落的装备必须是<=玩家等级阶段的状态，例如70级玩家掉80级装备肯定有问题
def isLowEquip(equipUseLevel, playerLevel):
    if (int(equipUseLevel / 10) == int(playerLevel / 10)):
        return 1
    elif (int(equipUseLevel / 10) < int(playerLevel / 10)):
        return 2
    else:
        return 3


# 鉴定职业是否合格，要求：
# 1. 掉落的蓝紫装必须是自己职业的
def checkEquipCarrer(handlePostmanData, playerCareer):
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute", None)
        # print("$$$$$$$",temp, playerCareer, (playerCareer in temp[3]) and (temp[1] in [3,4]))
        if ((playerCareer not in temp[3]) and (temp[1] in [3,4])):
            result.append(ikey)
        else:
            continue
    if result:
        print("副本中掉落的蓝紫装不是自己职业的问题装备编号： \n", result)
    else:
        print("本次统计结果中不存在掉落的蓝紫装不是自己职业的问题。")


# 鉴定副本中不能掉落已经鉴定的金装
def checkGoldEquip(handlePostmanData):
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute", None)
        if (temp[5] == 2 and temp[1] in [6,7]):
            result.append(ikey)
        else:
            continue
    if result:
        print("本次统计中副本中掉落的已鉴定装备的编号是： \n", result)
    else:
        print("本次统计中没有出现副本中掉落已鉴定金装的问题。")


# 鉴定掉落的装备的性别与玩家性别是否符合
def checkGender(handlePostmanData, playerSex):
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute")
        if (temp[2] == 0) or (temp[2] == playerSex):
            continue
        else:
            result.append(ikey)

    if result:
        print("本次统计中出现掉落装备与玩家性别不匹配的装备编号是：\n", result)
    else:
        print("本次统计中没有出现掉落装备与玩家性别不匹配的情况。")
    return result


# 统计装备总数量
def getTotolEquipNum(handelPostmanData):
    totolNum = 0
    for ikey, ivalue in handelPostmanData.items():
        for i, num in ivalue.items():
            if (i == "amount"):
                totolNum += num
    return totolNum


# 统计装备品质，分为三个字典，[{低蓝:x, 低紫:y, 低金:z, 低红:m}, {蓝:x, 紫:y, 金:z, 红:m},
# {高蓝:x, 高紫:y, 高金:z, 高红:m}]
def getEquipQuality(handlePostmanData, playerLevel):
    result = {}
    qualityList = ["蓝","紫","金", "红"]
    lowQuality = generateDict(qualityList)
    normalQuality = generateDict(qualityList)
    highQuality = generateDict(qualityList)
    qualityDict = {3: "蓝", 4: "紫", 6: "金", 7: "红"}
    bugEquip = {"low":[], "high":[]}     # 副本中掉落了低级的蓝紫装备时，副本中掉落了高级的蓝紫金红装备时，记录装备编号

    for ikey, ivalue in handlePostmanData.items():
       print("$$$$$$$$$$$$$$",ikey, ivalue)
       temp = ivalue.get("attribute", None)
       flag = isLowEquip(temp[4], playerLevel)
       if flag == 1:
           normalQuality[qualityDict[temp[1]]] += ivalue.get("amount", 0)
       elif flag == 2:
           lowQuality[qualityDict[temp[1]]] += ivalue.get("amount", 0)
           if temp[1] in [3,4]:
               bugEquip["low"].append(ikey)
       else:
           highQuality[qualityDict[temp[1]]] += ivalue.get("amount", 0)
           if temp[1] in [3,4,6,7]:
               bugEquip["high"].append(ikey)
    result["low"] = lowQuality
    result["normal"] = normalQuality
    result["high"] = highQuality
    return result, bugEquip

# 生成新的字典1
def generateDict(list1):
    newDict = {}
    for i in list1:
        newDict[i] = 0
    return newDict

# 生成新的字典1
def generateDict2(list2, list1):
    newDict = {}
    for i in list2:
        newDict[i] = generateDict(list1)
    return newDict


# 装备部位统计，分别统计出每个部位的装备品质
def getEquipLocalQuality(handelPostmanData):
    partDict = {1: "武器", 2: "手套", 3: "衣服", 4: "裤子", 5: "腰带", 6: "鞋子", 7: "护符", 8: "头饰"}
    partList = ["武器", "手套", "衣服", "裤子", "腰带", "鞋子", "护符", "头饰"]
    qualityDict = {3: "蓝", 4: "紫", 6: "金", 7: "红"}
    qualityList = ["蓝", "紫", "金", "红"]
    result = generateDict2(partList, qualityList)
    # print("***********", result)
    for ikey, ivalue in handelPostmanData.items():
        temp = ivalue.get("attribute", None)
        result[partDict[temp[0]]][qualityDict[temp[1]]] += 1
    return result


# 判断字典中的子字典是否为空
def isDictNull(dict1):
    flag = False
    for ikey, ivalue in dict1.items():
        if not ivalue:
            continue
        else:
            flag = True
    return flag




