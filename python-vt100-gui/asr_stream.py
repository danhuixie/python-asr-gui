# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
# from pyvoiceai import *
from app_asr_base_api import *
from app_auth_api import *
import numpy as np
import time, wave
import threading
import pyaudio
# from pyaudio import PyAudio, paInt16
from multiprocessing import Queue, Process

"""
    辅助内部工具，ASR实时识别
"""
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s-%(filename)s,[%(name)s:%(funcName)s:%(lineno)d] [%(levelname)s]:%(message)s")

# V_BASE_URL = "https://192.168.0.100:28072"
V_BASE_URL = "https://cloud.voiceaitech.com:8072"
V_APP_ID = "000eacad8a56440fac5f0b8aed07ab48"
V_APP_SECRET = "222eacad8a56440fac5f0b8aed07ab48"

auth = AppAuthAPI(V_BASE_URL, V_APP_ID)
auth.app_auth_get(V_APP_SECRET)
auth.app_auth_token_get()

def get_token():
    auth.app_auth_token_refresh()
    token = auth.get_access_token()
    return token

class RealTimeStreamAsr():
    def __init__(self, callback = None, callback_args = None):
        # open a pyAudio stream
        self.fs = 16000
        self.pa = pyaudio.PyAudio()
        self.block_samples = self.fs
        self.chunk = self.fs // 10
        # try: 
        #     self.stream_info = pyaudio.PaMacCoreStreamInfo(pyaudio.PaMacCoreStreamInfo.paMacCoreConversionQualityHigh)
        #     self.stream = None
        #     # self.stream = self.pa.open(format = pyaudio.paInt16, channels = 1, rate = self.fs, input = True, 
        #     #                             frames_per_buffer = self.chunk, input_host_api_specific_stream_info = stream_info)
        # except AttributeError:
        #     print("Could not find PaMacCoreStreamInfo")
        
        # open a websocket for stream asr
        self.websockethost = "wss://cloud.voiceaitech.com:8072/api/app/asr/streaming"
        auth = AppAuthAPI(V_BASE_URL, V_APP_ID)
        auth.app_auth_get(V_APP_SECRET)
        auth.app_auth_token_get()
        auth.app_auth_token_refresh()
        self.auth_token = auth.get_access_token()
        self.callback = callback
        self.callback_args = callback_args
        # self.ws = ASRBaseClient(url = self.websockethost, app_id = V_APP_ID, token = self.auth_token, sample_rate = self.fs, 
        #                         model_type = MODEL_ASR_POWER, func = self.callback, args = self.callback_args)
        
        # recording flag
        self.RecordingFlag = False
        self.mutex = threading.Lock()
        
    def __del__(self):
        if self.pa is not None:
            self.pa.terminate()
    
    def start(self, filename):
        if self.RecordingFlag:
             return
        # filename = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
        # print("filename:%s"%filename)
        self.ws = ASRBaseClient(url = self.websockethost, app_id = V_APP_ID, token = self.auth_token, sample_rate = self.fs, 
                                model_type = MODEL_ASR_POWER, func = self.callback, args = self.callback_args)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.fs)
        self.RecordingFlag = True
        self.ws.connect()
        
        # self.stream = self.pa.open(format = pyaudio.paInt16, channels = 1, rate = self.fs, input = True, 
        #                            frames_per_buffer = self.chunk, input_host_api_specific_stream_info = self.stream_info)
        self.stream = self.pa.open(format = pyaudio.paInt16, channels = 1, rate = self.fs, input = True,frames_per_buffer = self.chunk)
        while True:
            string_data = []
            for i in range(0, int(self.block_samples / self.chunk)):
                chunk_data = self.stream.read(self.chunk)
                string_data.append(chunk_data)
            wf.writeframes(b''.join(string_data))
            audio_data = np.fromstring(b''.join(string_data), dtype = np.short)
            # audio_data *= 4
            # self.ws.diy_send_binary(audio_data)
            if self.ws._is_closed:
                self.ws.connect()
            th1 = threading.Thread(target = self.ws.diy_send_binary, args=(audio_data,))
            th1.start()
            if not self.RecordingFlag:
                break
        
        self.stream.stop_stream()
        self.stream.close()
        wf.close()
        time.sleep(1)
        self.ws.close()
        self.ws = None
    
    def stop(self):
        if self.mutex.acquire():
            self.RecordingFlag = False
            self.mutex.release()

def callback(result, callback_args):
    print("Online Result:%s"%result)

if __name__ == '__main__':
    stream_asr = RealTimeStreamAsr(callback)
    filename = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
    th1 = threading.Thread(target = stream_asr.start, args = (filename,))
    th1.start()
    time.sleep(6)
    stream_asr.stop()
    time.sleep(2)
    th1 = threading.Thread(target = stream_asr.start, args = (filename,))
    th1.start()
    time.sleep(6)
    stream_asr.stop()
