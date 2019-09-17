# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from flask import Flask, render_template, request

class TaskManager(object):

    """
    给模版匹配对应的函数
    """
    @classmethod
    def task_response(cls, task, words, arcs_dict,postags):
        answer = ""
        if task == 'task_SBV_ATT_POB':
            answer = cls.answer_SBV_ATT_POB(words, arcs_dict,postags)

        return answer

    @classmethod
    def answer_SBV_ATT_POB(cls, words, arcs_dict,postags):
        flag = False
        att_index = 0
        for sub_arcs in arcs_dict:
            keys = sub_arcs.keys()
            if 'ATT' in keys:
                for att in range(len(sub_arcs['ATT'])):
                    if sub_arcs['ATT'][att] == 'r':
                        flag = True
                        att_index = att
                        break
                if flag:
                    break
            if flag:
                break
            if 'SVB' in keys:
                sub_arcs['SVB']

        if flag:
            uri = "https: // api.ownthink.com / kg / knowledge?entity="+








