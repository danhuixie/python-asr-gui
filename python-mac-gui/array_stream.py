# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
# from pyvoiceai import *
from app_asr_base_api import *
from app_auth_api import *
import numpy as np
import time, wave
import threading, ctypes
# import pyaudio
# from pyaudio import PyAudio, paInt16
# from multiprocessing import Queue, Process


# V_BASE_URL = "https://192.168.0.100:28072"
V_BASE_URL = "https://cloud.voiceaitech.com:8072"
V_APP_ID = "000eacad8a56440fac5f0b8aed07ab48"
V_APP_SECRET = "222eacad8a56440fac5f0b8aed07ab48"

# auth = AppAuthAPI(V_BASE_URL, V_APP_ID)
# auth.app_auth_get(V_APP_SECRET)
# auth.app_auth_token_get()

# def get_token():
#     auth.app_auth_token_refresh()
#     token = auth.get_access_token()
#     return token

class RealTimeArrayStreamAsr():
    def __init__(self, callback = None, callback_args = None):
        self.fs = 16000
        # self.block_samples = self.fs
        # self.chunk = self.fs // 10
        self.array_dll = ctypes.CDLL("libxmos-spicax-py.dylib")
        
        # open a websocket for stream asr
        self.websockethost = "wss://cloud.voiceaitech.com:8072/api/app/asr/streaming"
        auth = AppAuthAPI(V_BASE_URL, V_APP_ID)
        auth.app_auth_get(V_APP_SECRET)
        auth.app_auth_token_get()
        auth.app_auth_token_refresh()
        self.auth_token = auth.get_access_token()
        self.callback = callback
        self.callback_args = callback_args
        # self.ws = ASRBaseClient(url = websockethost, app_id = V_APP_ID, token = auth_token, sample_rate = self.fs, 
        #                         model_type = MODEL_ASR_POWER, func = callback, args = callback_args)
        
        # recording flag
        self.RecordingFlag = False
        self.mutex = threading.Lock()
    
    def start(self, filename):
        if self.RecordingFlag :
            return
        self.ws = ASRBaseClient(url = self.websockethost, app_id = V_APP_ID, token = self.auth_token, sample_rate = self.fs, 
                                model_type = MODEL_ASR_POWER, func = self.callback, args = self.callback_args)
        py_filename = filename[0:-4] + "-py.wav"
        wf = wave.open(py_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.fs)
        self.RecordingFlag = True
        self.ws.connect()
        
        # print("before StartRecording")
        # device_name = "Array"
        self.array_dll.StartRecording(filename.encode())
        # print("after StartRecording")
        string_data = bytes(self.fs * 2);
        # print(string_data)
        while True:
            # print(num)
            res = self.array_dll.ReadPcm(string_data, self.fs)
            audio_data = np.fromstring(string_data, dtype = np.short)
            audio_data1 = audio_data[0 : res-1]
            string_data1 = audio_data1.tostring()
            wf.writeframes(string_data1)
            if self.ws._is_closed:
                self.ws.connect()
            th1 = threading.Thread(target = self.ws.diy_send_binary, args=(audio_data1,))
            th1.start()
            # if self.mutex.acquire():
            if not self.RecordingFlag:
                # self.mutex.release()
                break
        wf.close()
        print("recording stop")
        self.array_dll.Stop()
        time.sleep(2)
        self.ws.close()
        self.ws = None
        # self.ws = ASRBaseClient(url = websockethost, app_id = V_APP_ID, token = auth_token, sample_rate = self.fs, 
        #                         model_type = MODEL_ASR_POWER, func = callback, args = callback_args)
    
    def stop(self):
        # if self.mutex.acquire():
        # self.array_dll.Stop()
        self.RecordingFlag = False
            # self.mutex.release()

def callback(result, callback_args):
    print("Online Result:%s"%result)

if __name__ == '__main__':
    stream_asr = RealTimeArrayStreamAsr(callback)
    filename = "./data/" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
    print(filename)
    th1 = threading.Thread(target = stream_asr.start, args = (filename,))
    th1.start()
    time.sleep(6)
    stream_asr.stop()
    time.sleep(3)
    filename = "./data/" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
    th2 = threading.Thread(target = stream_asr.start, args = (filename,))
    th2.start()
    time.sleep(10)
    stream_asr.stop()
