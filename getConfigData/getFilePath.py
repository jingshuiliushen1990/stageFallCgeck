# -*- coding:utf-8 -*-

import os

judgeList = ["AI_任务列表.xls", "CBT充值返还.xls", "C场景背景音效.xls", "enumerate.xls", "C错误码.xls",
             "D道具获取指引.xls", "H魂卡秘境.xls","W物品背包定义.xls", "zhangjingwen"]

# 读取文件获得文件路径，对不正确的路径分别返回不同的结果
def isRightFilePath(filePath):
    # 对于路径中有中文的可以用这种方式保证路径的正确，比较重要
    filePath = filePath.encode("gbk").decode("utf-8")

    # filePath = filePath.replace('\\', "\\\\")
    # print("&&&&&&", filePath)
    if ((filePath == None) or (filePath == '') or (not os.path.exists(filePath)) or
            (os.path.exists(filePath) and (not judgeFilePath(filePath)))):
        return False

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
    print(isRightFilePath("E:\M1_SVN\Market_build\lss\config\\resource"))