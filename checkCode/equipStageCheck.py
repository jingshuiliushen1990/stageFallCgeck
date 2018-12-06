# -*- coding:utf-8 -*-

from checkCode.baseClass import commonBase
import requests
import json
import re
from checkCode.universalApi import *


class equipStage(commonBase):
    """用来计算装备秘境中掉落金装的概率"""

    def __init__(self, checkType, stageId, career, gender, lv, count, normalGoldFallRate, lowGoldFallRate, errorRange):
        super(equipStage, self).__init__(lv, career, gender, count, checkType)
        self.stageId = stageId
        self.normalGoldFallRate = normalGoldFallRate
        self.lowGoldFallRate = lowGoldFallRate
        self.errorRange = errorRange

    def getStageId(self):
        return self.stageId

    def setStageId(self, newStageId):
        self.stageId = newStageId

    def getNormalGoldFallRate(self):
        return self.normalGoldFallRate

    def setNormalGoldFallRate(self, newNormalGoldFallRate):
        self.normalGoldFallRate = newNormalGoldFallRate

    def getLowGoldFallRate(self):
        return self.lowGoldFallRate

    def setLowGoldFallRate(self, newLowGoldFallRate):
        self.lowGoldFallRate = newLowGoldFallRate

    def getErrorRange(self):
        return self.errorRange

    def setErrorRange(self, newErrorRange):
        self.errorRange = newErrorRange


    def getPostmanKeyDict(self):
        postmanKeyDict = {}
        postmanKeyDict["stage_id"] = self.stageId
        postmanKeyDict["count"] = self.count
        postmanKeyDict["lv"] = self.lv
        postmanKeyDict["career"] = self.career
        postmanKeyDict["gender"] = self.gender

        return postmanKeyDict

    def getPostmanData(self):
        httpAddr = commonBase.getHttpAddr(self)
        try:
            postmanData = requests.post(httpAddr, data=self.getPostmanKeyDict())
            # print("**********", postmanData.text)
            return postmanData.text
        except:
            print("服务器连接不上，请检查连接！！！")
            exit(0)
            return False

    def getUsefulPostmanData(self):
        postmanData = self.getPostmanData()
        if not judgeJsonStr(postmanData):
            return False
        else:
            return json.loads(postmanData).get("data", None)


    # 处理postman 数据，得到便于统计的形式，然后进行统计
    def initPostmanData(self, allData):
        result = {}
        tempData = self.getUsefulPostmanData()
        if tempData:
            equipData1 = initEquipData(allData)
            for i in tempData:
                checkResult = isEquip(equipData1, i.get("id"))
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


# 判断postman返回的数据是不是json格式，防止返回是 ：<Response [404]>，导致后面无法继续进行
def judgeJsonStr(testStr):
    if testStr.startswith('{') and testStr.endswith('}'):
        return True
    else:
        return False


# 判断给定的物品编号是不是装备，是的话返回该装备的部位，品质，性别，职业，使用等级， 不是时返回False
def isEquip(equipData, goodId):
    goodIdInfo = equipData.get(goodId, None)
    if goodIdInfo:
        result = []
        if goodIdInfo["type"] != 25:
            result.append(goodIdInfo.get("sub_type"))
            result.append(goodIdInfo.get("quality"))
            result.append(goodIdInfo.get("gender"))
            result.append(goodIdInfo.get("careers"))
            result.append(goodIdInfo.get("use_level"))
            result.append(goodIdInfo.get("type"))
        else:
            result.append(goodIdInfo.get("sub_type"))
            result.append(goodIdInfo.get("quality"))
            result.append(0)
            result.append(goodIdInfo.get("careers"))
            result.append(getSymbolUseLevel(goodIdInfo.get("purpose")))
            result.append(goodIdInfo.get("type"))
        return result
    else:
        return False


# 获得徽记的使用等级，装备表没有，只能通过描述来进行拆分获得
# 道具使用描述“用于把60级金色神官靴子升级到70级的徽记”后面的70级是使用等级，可以用正则表达式来拆分得到
def getSymbolUseLevel(purposeStr):
    levelList = re.findall('\d+', purposeStr)
    return int(levelList[-1])


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
    checkResult = {}
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute", None)
        # print("$$$$$$$",temp, playerCareer, (playerCareer in temp[3]) and (temp[1] in [3,4]))
        if ((playerCareer not in temp[3]) and (temp[1] in [3,4])):
            result.append(ikey)
        else:
            continue
    if result:
        checkResult["副本中掉落的蓝紫装不是自己职业的问题装备编号："] = result
        # print("副本中掉落的蓝紫装不是自己职业的问题装备编号： \n", result)
    else:
        checkResult["本次统计结果中不存在掉落的蓝紫装不是自己职业的问题"] = {}
        # print("本次统计结果中不存在掉落的蓝紫装不是自己职业的问题。")
    return checkResult

# 鉴定副本中不能掉落已经鉴定的金装
def checkGoldEquip(handlePostmanData):
    checkResult = {}
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute", None)
        if (temp[5] == 2 and temp[1] in [6,7]):
            result.append(ikey)
        else:
            continue
    if result:
        checkResult["本次统计中副本中掉落的已鉴定装备的编号是："] = result
        # print("本次统计中副本中掉落的已鉴定装备的编号是： \n", result)
    else:
        checkResult["本次统计中没有出现副本中掉落已鉴定金装的问题"] = {}
        # print("本次统计中没有出现副本中掉落已鉴定金装的问题。")
    return checkResult

# 鉴定掉落的装备的性别与玩家性别是否符合
def checkGender(handlePostmanData, playerSex):
    checkResult = {}
    result = []
    for ikey, ivalue in handlePostmanData.items():
        temp = ivalue.get("attribute")
        if (temp[2] == 0) or (temp[2] == playerSex):
            continue
        else:
            result.append(ikey)
    if result:
        checkResult["本次统计中出现掉落装备与玩家性别不匹配的装备编号是："] = result
        # print("本次统计中出现掉落装备与玩家性别不匹配的装备编号是：\n", result)
    else:
        checkResult["本次统计中没有出现掉落装备与玩家性别不匹配的情况"] = {}
        # print("本次统计中没有出现掉落装备与玩家性别不匹配的情况。")
    return checkResult


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

# 生成新的字典
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
        result[partDict[temp[0]]][qualityDict[temp[1]]] += ivalue.get("amount",0)
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


# 检查每个部位的装备掉落去年情况，头饰是任何品质的都不掉落，其余的是掉落蓝紫金品质，红品质的是任何部位都不能掉落
def checkEquipLocalQuality(equipQualityDict):
    checkResult = {}
    tempResult = {}
    for ikey, ivalue in equipQualityDict.items():
        if (ikey != "头饰"):
            if checkDictIsNull(ivalue):
                tempResult[ikey] = checkDictIsNull(ivalue)
            else:
                continue
        else:
            if not checkHeadWear(ivalue):
                checkResult["副本不应该掉落头饰，但是掉落了："] = ivalue
            else:
                checkResult["副本没有掉落头饰，是正常的："] = {}
                continue
    if tempResult:
        checkResult["装备掉落有问题，某个部位掉落数量为0，请检查："]= tempResult
    else:
        checkResult["单部位装备掉落没有问题，除头饰外各品质的都有掉落："] = {}
    return checkResult


# 检查除头饰部位以外的其他部位掉落，红色必须为0，其他部位必须不能为0，满足时返回True，否者返回False
def checkDictIsNull(iDict):
    result = {}
    for ikey, ivalue in iDict.items():
        if (ivalue == 0 and ikey != "红") or (ivalue != 0 and ikey == "红"):
            result[ikey] = ivalue
        else:
            continue
    return result


# 检查头饰掉落，有掉落是反馈False，没有掉落时返回True
def checkHeadWear(iDict):
    for ikey, ivalue in iDict.items():
        if ivalue != 0:
            return False
        else:
            continue
    return True


# 检查金装掉落概率
def checkFallRate(equipQualityDict, normalFallRate, lowFallRate, count, errorRange):
    checkResult = {}
    equipFallRataDict = getFallRate(equipQualityDict, count)
    for ikey, ivalue in equipFallRataDict.items():
        if ikey == "low":
            if not checkRate(ivalue, lowFallRate, errorRange):
                checkResult["低级金装掉落概率有问题："] = ivalue
            else:
                checkResult["低级金装掉落概率没有问题："] = {}
                continue
        elif ikey == "normal":
            if not checkRate(ivalue, normalFallRate, errorRange):
                checkResult["正常金装掉落概率有问题："] = ivalue
            else:
                checkResult["正常金装掉落概率没有问题："] = {}
                continue
        else:
            continue
    return checkResult


# 转化获得金装的数目变为掉落概率
def getFallRate(equipQualityDict, count):
    checkResult = {}
    for ikey, ivalue in equipQualityDict.items():
        temp = {}
        for ikey1, ivalue1 in ivalue.items():
            temp[ikey1] = round(ivalue1/count, 5)
        checkResult[ikey] = temp

    return checkResult


# 检查不同品种的装备，分为low 和normal的来比对
def checkRate(equipFallRataDict, fallRate, errorRange):
    equipFallRate = equipFallRataDict.get("金", 0)
    lowFallRate, highFallRate = getFallRateRange(fallRate, errorRange)
    if (equipFallRate >= lowFallRate and equipFallRate <= highFallRate):
        return True
    else:
        return False


# 计算出容错率下的金装掉落范围，计算方法，容错率为 +-5%的时候， 实际范围是 掉率x(95% ~~ 105%)，
# 原来的掉率是1%的话，那实际掉落是 0.95% ~~ 1.05%，返回形式是元组
def getFallRateRange(fallRate, errorRange):
    return round(fallRate * (1 - errorRange), 5), round(fallRate * (1 + errorRange), 5)


# 对装备本掉落进行判断，假如掉落有低等级的蓝紫装或者掉落有高等级的蓝紫金红装备，返回True，反之返回False
def judgeWrongFall(iDict):
    result = {}
    if isDictNull(iDict):
        result["副本有掉落低等级蓝紫装或者掉落高等级蓝紫金红装："] = iDict
    else:
        result["副本没有掉落低等级蓝紫装和高等级蓝紫金红装备的情况"] = {}
    return result


def equipStageFallCheck(termList, allData):
    newResult = {}
    result = {}

    equipStageObj = equipStage(int(termList[0]), int(termList[1]), int(termList[3]), int(termList[4]),
                               int(termList[5]), int(termList[6]), termList[8], termList[9], termList[10])

    postmanData = equipStageObj.initPostmanData(allData)

    careerCheck = checkEquipCarrer(postmanData, equipStageObj.getCareer())
    undefineGoidEquip = checkGoldEquip(postmanData)
    genderCheck = checkGender(postmanData, equipStageObj.getGender())
    equipQualityNum, bugEquip = getEquipQuality(postmanData, equipStageObj.getLv())
    getEquipLocalQualityData = getEquipLocalQuality(postmanData)
    checkLocalEquipFall = checkEquipLocalQuality(getEquipLocalQualityData)
    equipFallRate = getFallRate(equipQualityNum, equipStageObj.getCount())
    checkFallRateRestlt = checkFallRate(equipQualityNum, equipStageObj.getNormalGoldFallRate(),
                        equipStageObj.getLowGoldFallRate(), equipStageObj.getCount(), equipStageObj.getErrorRange())

    result["装备掉落概率"] = equipFallRate
    result["各部位装备掉落数量"] = getEquipLocalQualityData
    result.update(checkFallRateRestlt)
    result.update(careerCheck)
    result.update(undefineGoidEquip)
    result.update(genderCheck)
    result.update(judgeWrongFall(bugEquip))
    result.update(checkLocalEquipFall)

    newResult[tuple(termList)] = result

    return newResult


if __name__ == "__main__":
    from getConfigData.loadAllDictData import *
    filePath = "E:\\M1_SVN\\Market_build\\lss\\config\\resource\\"
    keyList = [1.0, 321018.0, '', 6.0, 1.0, 75.0, 1000.0, '', 0.02, 0.005, 0.005]
    keyList1 = [1, 321002, '', 6, 1, 65, 1000, '', 0.02]
    equipStageFallCheck(keyList, getLocalConfigData(filePath))



