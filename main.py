#-*- coding:utf-8 -*-

from rwFile.getExcelData import *
from checkCode.equipStageCheck import *
from getConfigData.loadAllDictData import *
import threading


excelObj = getExcelData("config.xlsx")
constData = excelObj.getSheetData("常量配置")
checkData = excelObj.getSheetData("待检查副本配置")

global allData
if constData["isUseLocalData"]:
    allData = getLocalConfigData(constData["configDataPath"])
else:
    allData = getSvnConfigData()

threadNum = int(constData["processLimit"])


class myThread(threading.Thread):
    def __init__(self, func, args=()):
        super(myThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


# 跟进进程数量拆分测试的配置数据，便于均衡的分配到各个线程，并且保证分配后的数据长度 <= 1
def splitTestData(allTeamList, threadNum):
    result = []
    for i in range(threadNum):
        result.append([])
    for i in range(len(allTeamList)):
        result[i%threadNum].append(allTeamList[i])
    return result


# 根据检查类型执行不同的检查函数
def findFunction(termlist, allConfigData):
    result = {}
    if termlist[0] == 1:
        result = equipStageFallCheck(termlist, allConfigData)
    else:
        print("hello world")
        pass
    # print("@@@@@@@@", result)
    return result


# 处理组数据
def handleGroupData(groupTermList, allConfigData):
    tempResult = {}
    for iTerm in groupTermList:
        if iTerm:
            tempResult.update(findFunction(iTerm, allConfigData))
        else:
            pass
    return tempResult


def processTestData(allTermList, threadNum, allConfigData):
    allResult = {}
    threadList = []
    newSplitTestData = splitTestData(allTermList, threadNum)
    for i in range(threadNum):
        t = myThread(handleGroupData, args=(newSplitTestData[i], allConfigData))
        threadList.append(t)
        t.start()

    for t in threadList:
        t.join()
        # print("QQQQQQQQQ", t.get_result())
        allResult.update(t.get_result())

    print("WWWWWWWWWWW", allResult)
    return allResult


# 测试一下顺序执行时的耗时，查看一下多线程的时间节省
def test(allTermList, allConfigData):
    allResult = {}
    for i in allTermList:
        allResult.update(findFunction(i, allConfigData))

    print("########", allResult)
    return allResult


# 分类获得检查结果的key值，然后加到列表中
def getKeyList(iDict):
    keyList = []
    for ikey, ivalue in iDict.items():
        if ikey[0] in [1, 3]:
            if ikey[1] not in keyList:
                keyList.append(ikey[1])
            else:
                continue
        if ikey[0] == 2:
            newKey = str(ikey[1]) + "--" + str(ikey[2])
            if newKey not in keyList:
                keyList.append(newKey)
            else:
                continue
        else:
            if ikey[1] not in keyList:
                keyList.append(ikey[1])
    return keyList

# 对得到的keyList 进行处理，然后得到一个{key1:{},key2:{},……}类型的字典
def getKeyDict(iList):
    keyDict = {}
    for i in iList:
        keyDict[i] = {}
    return keyDict


# 对结果进行预处理，便于发邮件和把结果写到excel文件中
def initResultData(iDict):
    newResult = {}
    keyList = getKeyList(iDict)
    keyDict = getKeyDict(keyList)
    for ikey, ivalue in iDict.items():
        temp = {}
        temp[ikey] = ivalue
        if ikey[0] in [1,3]:
            keyDict[ikey[1]].update(temp)
        elif ikey[0] == 2:
            newkey = str(ikey[1])+"--"+ str(ikey[2])
            keyDict[newkey].update(temp)
        else:
            keyDict[ikey[1]].update(temp)

    for ikey1, ivalue1 in keyDict.items():
        for ikey2, ivalue2 in ivalue1.items():
            if ikey2[0] == 1:
                newResult["装备秘境 "+str(ikey1)+" 的检查结果"] = ivalue1
                continue
            elif ikey2[0] == 2:
                newResult["魂卡秘境 "+str(ikey1)+" 的检查结果"] = ivalue1
                continue
            elif ikey2[0] == 3:
                newResult["普通副本 "+str(ikey1)+" 的检查结果"] = ivalue1
                continue
            else:
                newResult["宝箱 "+str(ikey1)+" 的检查结果"] = ivalue1
                continue

    return newResult




if __name__ == "__main__":
    processTestData(checkData, threadNum, allData)
    # test(checkData, allData)


