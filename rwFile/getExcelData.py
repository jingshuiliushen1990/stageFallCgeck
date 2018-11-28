# -*- coding:utf-8 -*-

import xlrd
import xlwt
import os
import sys


class getExcelData(object):
    """用来读取给定的excel数据，传入的参数是 excelName,
    后续可以传入sheetName 来获得sheet中的数据"""
    def __init__(self, excelName):
        self.excelName = excelName

    def createExcelObj(self):
        filePath = "./"+str(self.excelName)
        excelBook = xlrd.open_workbook(filePath)
        return excelBook

    # 传入sheetName 得到sheet中的数据，按照行列表的形式返回
    def getSheetData(self, sheetName):
        result = []
        excelBook = self.createExcelObj()
        initSheetData = excelBook.sheet_by_name(sheetName)
        for i in range(initSheetData.nrows):
            result.append(initSheetData.row_values(i))
        if sheetName == "请求URL配置":
            newResult = joinUrlStr(result[1:])
            return newResult
        elif sheetName == "邮件配置":
            newResult = joinEmailStr(result[1:])
            return newResult
        elif sheetName == "常量配置":
            return creatConstKeyDict(result[1:])
        else:
            return result[1:]


# 对本地数据配置 和 使用本地数据标志进行处理，目前是list中嵌套list， 读数据时有点麻烦，直接返回具体数值
# def getUsefulData(ilist):
#     if len(ilist) == 1:
#         return False
#     return ilist[1][0]


# 把常量配置分页中的数据生成可用的字典，便于后面的使用与校验
def creatConstKeyDict(ilist):
    resultDict = {}
    for i in ilist:
        resultDict[i[0]] = i[1]
    return resultDict


# 拼接postman 请求地址，配置中是分开配置的，便于将来修改
def joinUrlStr(urlList):
    resultDict = {}
    if not urlList:
        return False
    else:
        for iUrl in urlList:
            resultDict[iUrl[0]] = joinElem2Url(iUrl[1:4])
        return resultDict


# 拼接几个信息组成url
def joinElem2Url(ilist):
    urlAddr = ''
    for i in range(len(ilist)):
        if i == 0:
            if ilist[i].endswith('/'):
                urlAddr += ilist[i]
            else:
                urlAddr += ilist[i] + '/'
        elif i == 1:
            urlAddr += str(int(ilist[i]))
        else:
            urlAddr += ilist[i]
    return urlAddr


# 拼接邮件列表，目前邮件中的信息都是单独的列表，整合到单独的列表中
def joinEmailStr(emailList):
    # print("++++++++++", emailList)
    if not emailList:
        return False
    else:
        newEamilDict = {}
        inboxList = []
        outbox = []

        # for iEamil in emailList:
        #     newEamilList.append(checkEamilValidity(iEamil[0]))

        for i in range(len(emailList)):
            if (i == 0):
                outbox.append(checkEamilValidity(emailList[i][0]))
                outbox.append(emailList[i][1])
            elif (i == 1):
                continue
            else:
                inboxList.append(checkEamilValidity(emailList[i][0]))
        newEamilDict["outbox"] = outbox
        newEamilDict["inboxList"] = inboxList

        return newEamilDict


# 去掉配置的游戏数据中的空格或者逗号，分号，防止发邮件时检查到邮件地址不合格发不出去
def checkEamilValidity(iEamil):
    tempEamil = iEamil.strip()
    tempEamil = tempEamil.strip('.')
    tempEamil = tempEamil.replace(' ', '')
    tempEamil = tempEamil.replace(',', '')
    tempEamil = tempEamil.replace(';', '')
    return tempEamil


if __name__ == "__main__":
    x = getExcelData("../config.xlsx")
    print("%%%%%%%", x.getSheetData("待检查副本配置"))
    print("$$$$$$$", x.getSheetData("请求URL配置"))
    print("UUUUUUU", x.getSheetData("常量配置"))
    print("BBBBBBB", x.getSheetData("邮件配置"))