# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from cbot import AIMLUtil
from cbot import NLPUtil

def chat(question_str):

    words,pattern,arcs_dict,postags = NLPUtil.get_sentence_pattern(question_str)
    aiml_reponse = AIMLUtil.response(pattern)




if __name__ == '__main__':
    AIMLUtil()
    NLPUtil('ltp_data_v3.4.0')

    while True:
        question_str = input('User:')
        if question_str == 'exit':
            break
        else:
            ans = chat(question_str)
            print(ans)








