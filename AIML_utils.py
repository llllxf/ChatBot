# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from cbot import  aiml_cn

"""
AIML工具类
"""
class AIMLUtil(object):

    @classmethod
    def __init__(cls):

        cls.aiml_kernal = aiml_cn.Kernel()
        cls.aiml_kernal.learn('pattern.aiml')

    @classmethod
    def response(cls, question):
        aiml_response = cls.aiml_kernal.respond(question)
        return aiml_response


if __name__ == '__main__':
    AIMLUtil()
    ans = AIMLUtil.response("SBVVOB")
    #ans = AIMLUtil.response("SBVHEDPOB")

    print(ans)

