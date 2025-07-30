# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250529-100152
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
Program description
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
from LlmGenJson import LlmGenJson


def mainClassOne():
    o = LlmGenJson()
    # o._loadSystemPrompt('')
    # o._loadSystemPrompt('Translate_prompt')
    # o._loadSystemPrompt('Translate_stem')
    # o.test_strict_json_llm()
    # return
    # o.NaturalLanguageToJson('解析定时任务时间参数-v00', '凌晨6点30分打卡')  # v00 的确不行
    o.NaturalLanguageToJson('解析定时任务时间参数', '每天凌晨6点30分打卡')
    # o.NaturalLanguageToJson('解析定时任务时间参数', '凌晨6点30分打卡')


if __name__ == '__main__':
    mainClassOne()
