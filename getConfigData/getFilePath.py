# -*- coding:utf-8 -*-

import os

judgeList = ["AI_任务列表.xls", "CBT充值返还.xls", "C场景背景音效.xls", "enumerate.xls", "C错误码.xls", "D道具获取指引.xls",
             "D夺宝奇兵军衔.xls", "G公会-黑暗深渊.xls", "H魂卡秘境.xls","W物品背包定义.xls", "zhangjingwen"]

# 读取文件获得文件路径，对不正确的路径分别返回不同的结果
def getFilePath():
    path = open("../filePath.txt", 'r').read()
    # path = open("./filePath.txt", 'r').read()
    # print("path = ", path)
    # filePath = unicode(path, "utf-8")

    # 对于路径中有中文的可以用这种方式保证路径的正确，比较重要
    filePath = path.encode("gbk").decode("utf-8")
    # print("filepath = ", filePath)

    if (filePath == None) or (filePath == ''):
        return -1
    elif (not os.path.exists(filePath)):
        return -2
    elif (os.path.exists(filePath) and (not judgeFilePath(filePath))):
        return -3
    else:
        if filePath.endswith('\\') or filePath.endswith('/'):
            return filePath
        else:
            # print("*********",filePath+os.sep)
            return filePath+os.sep


# 对给定的文件路径进行判断
def judgeFilePath(filePath):
    for iName in judgeList:
        if iName in os.listdir(filePath):
            continue
        else:
            return False
    return True


if __name__ == "__main__":
    print(getFilePath())