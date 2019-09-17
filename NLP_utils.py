# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer


class NLPUtil(object):

    @classmethod
    def __init__(cls, model_path):

        cls.model_path = model_path

        """
        分词
        """
        cls.segmentor = Segmentor()
        cls.segmentor.load(os.path.join(cls.model_path, "cws.model"))
        """
        词性标注
        """
        cls.postagger = Postagger()
        cls.postagger.load(os.path.join(cls.model_path, "pos.model"))
        """
        句法依存分析
        """
        cls.parser = Parser()
        cls.parser.load(os.path.join(cls.model_path, "parser.model"))

        """
        疑问代词
        """
        cls.Interrogative_pronouns = ['哪里','什么','怎么','哪','为什么','啥']

    """
    :describe 分词
    :arg 句子
    """
    @classmethod
    def cut_sentence(cls, sentence):
        words = cls.segmentor.segment(sentence)
        return words

    """
    :describe 词性分析
    :arg 分词列表
    """
    @classmethod
    def get_postag(cls, words):
        postags = cls.postagger.postag(words)
        return postags

    """
    :describe 句法依存
    :arg 分词列表, 词性列表
    """

    @classmethod
    def get_parse(cls, words, postags):
        parse = cls.parser.parse(words, postags)
        return parse

    """
    :describe 
    得到问题对应的模版
    1.先对问题分词
    2.得到每个分词对应的词性
    3.得到句法依存分析树

    :arg 句子
    """
    @classmethod
    def get_sentence_pattern(cls, sentence):
        words = cls.cut_sentence(sentence)
        postags = cls.get_postag(words)
        arcs = cls.parser.parse(words, postags)
        arcs_dict = cls._build_sub_dicts(words,arcs)
        #print(arcs[1].head,arcs[1].relation)
        pattern = ""
        for i in range(len(words)):
            #print("i",i)
            for sub_dict in arcs_dict:
                keys = sub_dict.keys()
                for k in keys:
                   #print("k and sub_dict[k]",k,sub_dict[k])
                    if i in sub_dict[k]:
                        pattern += k
                        #print("i,pattern",i,pattern)
                        break
        return words,pattern,arcs_dict,postags

    @classmethod
    def extract(self, sentence):
        words = self.segmentor.segment(sentence)
        postags = self.postagger.postag(words)
        ner = self.recognizer.recognize(words, postags)
        arcs = self.parser.parse(words, postags)

        sub_dicts = self._build_sub_dicts(words, postags, arcs)
        for idx in range(len(postags)):

            if postags[idx] == 'v':
                sub_dict = sub_dicts[idx]
                # 主谓宾
                if 'SBV' in sub_dict and 'VOB' in sub_dict:
                    e1 = self._fill_ent(words, postags, sub_dicts, sub_dict['SBV'][0])
                    r = words[idx]
                    e2 = self._fill_ent(words, postags, sub_dicts, sub_dict['VOB'][0])
                    if self.clean_output:
                        self.out_handle.write("%s, %s, %s\n" % (e1, r, e2))
                    else:
                        self.out_handle.write("主谓宾\t(%s, %s, %s)\n" % (e1, r, e2))
                    self.out_handle.flush()
                # 定语后置，动宾关系
                if arcs[idx].relation == 'ATT':
                    if 'VOB' in sub_dict:
                        e1 = self._fill_ent(words, postags, sub_dicts, arcs[idx].head - 1)
                        r = words[idx]
                        e2 = self._fill_ent(words, postags, sub_dicts, sub_dict['VOB'][0])
                        temp_string = r + e2
                        if temp_string == e1[:len(temp_string)]:
                            e1 = e1[len(temp_string):]
                        if temp_string not in e1:
                            if self.clean_output:
                                self.out_handle.write("%s, %s, %s\n" % (e1, r, e2))
                            else:
                                self.out_handle.write("动宾定语后置\t(%s, %s, %s)\n" % (e1, r, e2))

                            self.out_handle.flush()

            # 抽取命名实体有关的三元组
            try:
                if ner[idx][0] == 'S' or ner[idx][0] == 'B':
                    ni = idx
                    if ner[ni][0] == 'B':
                        while len(ner) > 0 and len(ner[ni]) > 0 and ner[ni][0] != 'E':
                            ni += 1
                        e1 = ''.join(words[idx:ni + 1])
                    else:
                        e1 = words[ni]
                    if arcs[ni].relation == 'ATT' and postags[arcs[ni].head - 1] == 'n' and ner[
                        arcs[ni].head - 1] == 'O':
                        r = self._fill_ent(words, postags, sub_dicts, arcs[ni].head - 1)
                        if e1 in r:
                            r = r[(r.idx(e1) + len(e1)):]
                        if arcs[arcs[ni].head - 1].relation == 'ATT' and ner[arcs[arcs[ni].head - 1].head - 1] != 'O':
                            e2 = self._fill_ent(words, postags, sub_dicts, arcs[arcs[ni].head - 1].head - 1)
                            mi = arcs[arcs[ni].head - 1].head - 1
                            li = mi
                            if ner[mi][0] == 'B':
                                while ner[mi][0] != 'E':
                                    mi += 1
                                e = ''.join(words[li + 1:mi + 1])
                                e2 += e
                            if r in e2:
                                e2 = e2[(e2.idx(r) + len(r)):]
                            if r + e2 in sentence:
                                if self.clean_output:
                                    self.out_handle.write("%s, %s, %s\n" % (e1, r, e2))
                                else:
                                    self.out_handle.write("人名/地名/机构\t(%s, %s, %s)\n" % (e1, r, e2))

                                self.out_handle.flush()
            except:
                pass

    """
    :decription: 为句子中的每个词语维护一个保存句法依存儿子节点的字典
    :args:
        words: 分词列表
        postags: 词性列表
        arcs: 句法依存列表
    """

    @classmethod
    def _build_sub_dicts(cls, words, arcs):
        sub_dicts = []
        for idx in range(len(words)):
            sub_dict = dict()
            for arc_idx in range(len(arcs)):
                """
                如果这个依存关系的头节点是该单词
                """
                if arcs[arc_idx].head == idx + 1:
                    if arcs[arc_idx].relation in sub_dict:
                        sub_dict[arcs[arc_idx].relation].append(arc_idx)
                    else:
                        sub_dict[arcs[arc_idx].relation] = []
                        sub_dict[arcs[arc_idx].relation].append(arc_idx)
            sub_dicts.append(sub_dict)

        return sub_dicts

    """
    :decription:完善识别的部分实体
    """

    def _fill_ent(self, words, postags, sub_dicts, word_idx):
        sub_dict = sub_dicts[word_idx]
        prefix = ''
        if 'ATT' in sub_dict:
            for i in range(len(sub_dict['ATT'])):
                prefix += self._fill_ent(words, postags, sub_dicts, sub_dict['ATT'][i])

        postfix = ''
        if postags[word_idx] == 'v':
            if 'VOB' in sub_dict:
                postfix += self._fill_ent(words, postags, sub_dicts, sub_dict['VOB'][0])
            if 'SBV' in sub_dict:
                prefix = self._fill_ent(words, postags, sub_dicts, sub_dict['SBV'][0]) + prefix

        return prefix + words[word_idx] + postfix
