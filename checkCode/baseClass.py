# -*-  coding:utf-8 -*-

class commonBase(object):
    """几个通用的属性，做成通用基类，便于其他父类继承"""

    # count代表通关次数，lv代表玩家等级，career代表玩家职业，gender 代表玩家性别
    def __init__(self, count, lv, career, gender):
        self.count = count
        self.lv = lv
        self.career = career
        self.gender = gender


