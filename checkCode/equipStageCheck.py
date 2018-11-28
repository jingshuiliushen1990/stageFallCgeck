# -*- coding:utf-8 -*-

from checkCode.baseClass import commonBase
import requests
import json


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




