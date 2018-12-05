# -*-  coding:utf-8 -*-

from rwFile.getExcelData import *

configData = getExcelData("../config.xlsx")

class commonBase(object):
    """几个通用的属性，做成通用基类，便于其他父类继承"""

    # count代表通关次数，lv代表玩家等级，career代表玩家职业，gender 代表玩家性别
    def __init__(self, lv, career, gender, count, checkType):
        self.lv = lv
        self.career = career
        self.gender = gender
        self.count = count
        self.checkType = checkType

    def getLv(self):
        return self.lv

    def setLv(self, newLv):
        self.lv = newLv

    def getCareer(self):
        return self.career

    def setCareer(self, newCareer):
        self.career = newCareer

    def getGender(self):
        return self.gender

    def setGender(self, newGender):
        self.gender = newGender

    def getCount(self):
        return self.count

    def setCount(self, newCount):
        self.count = newCount

    def getChcekType(self):
        return self.checkType

    def setCheckType(self, newCheckType):
        self.checkType = newCheckType

    def getHttpAddr(self):
        httpAddr = configData.getSheetData("请求URL配置")[self.checkType]
        return httpAddr


