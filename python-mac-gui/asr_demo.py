# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
# from pyvoiceai import *
import sys
from app_asr import *

# 1.设置日志
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s-%(filename)s,[%(name)s:%(funcName)s:%(lineno)d] [%(levelname)s]:%(message)s")

# try:
#     File_Name = sys.argv[1]
# except:
#     File_Name = "./asrtxt.wav"


# # 5.辅助回调，可不用，这个只是辅助调试。
# def call_back_debug(t):
#     print("debug: %s" % t)

def run_asr(File_Name, call_back, call_back_par):
    # 2.主要配置
    # V_HOST = "wss://192.168.0.100:28072"
    # V_HOST = "ws://192.168.0.200:8070"
    # V_HOST = "wss://111.230.200.239:8072"
    V_HOST = "wss://cloud.voiceaitech.com:8072"
    V_APP_ID = "000eacad8a56440fac5f0b8aed07ab48"
    V_APP_SECRET = "222eacad8a56440fac5f0b8aed07ab48"

    # 3.新建一个客户端， 传入配置以及回调函数
    c = ASRClient(V_APP_ID, V_APP_SECRET, V_HOST, call_back, call_back_par)

    # 4.开始识别，识别过程为阻塞，会一直运行到识别结束，如果音频较长， 请传入回调函数进行观察
    # 16000             表示采样率
    # MODEL_ASR_POWER   是电力模型名，常量定义在sdk中
    # File_Name         需要识别的音频
    # 800               间歇时间，识别是实时识别，发送间歇800毫秒，当服务器性能良好，可以设置100毫秒
    txt = c.asr(16000, MODEL_ASR_POWER, File_Name, 100)
    return txt

# if __name__ == '__main__':
#     print("start")

#     # # 2.主要配置
#     # V_HOST = "wss://192.168.0.100:28072"
#     # V_HOST = "ws://192.168.0.200:8070"
#     # V_HOST = "wss://111.230.200.239:8072"
#     # V_HOST = "wss://cloud.voiceaitech.com:8072"
#     # V_APP_ID = "000eacad8a56440fac5f0b8aed07ab48"
#     # V_APP_SECRET = "222eacad8a56440fac5f0b8aed07ab48"

#     # # 3.新建一个客户端， 传入配置以及回调函数
#     # c = ASRClient(V_APP_ID, V_APP_SECRET, V_HOST, call_back_debug)

#     # # 4.开始识别，识别过程为阻塞，会一直运行到识别结束，如果音频较长， 请传入回调函数进行观察
#     # # 16000 			表示采样率
#     # # MODEL_ASR_POWER 	是电力模型名，常量定义在sdk中
#     # # File_Name 		需要识别的音频
#     # # 800 				间歇时间，识别是实时识别，发送间歇800毫秒，当服务器性能良好，可以设置100毫秒
#     # txt = c.asr(16000, MODEL_ASR_POWER, File_Name, 100)
#     txt = run_asr(File_Name)
#     print(txt)

#     # 5.可以再继续识别
#     # txt = c.asr(16000, MODEL_ASR_POWER, File_Name)
#     # print(txt)
