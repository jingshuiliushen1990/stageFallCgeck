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



if __name__ == "__main__":
    # print("%%%%%%%", constData)
    # print("UUUUUUU", checkData)
    # print("BBBBBBB", threadNum)
    processTestData(checkData, threadNum, allData)



