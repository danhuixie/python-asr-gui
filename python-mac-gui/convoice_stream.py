# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
from app_asr_base_api import *
from app_auth_api import *
import numpy as np
import time, wave
import threading, ctypes
import os

V_BASE_URL = "https://cloud.voiceaitech.com:8072"
V_APP_ID = "000eacad8a56440fac5f0b8aed07ab48"
V_APP_SECRET = "222eacad8a56440fac5f0b8aed07ab48"

class ConVoiceStreamAsr():
    def __init__(self, callback = None, callback_args = None):
        self.fs = 16000
        # self.block_samples = self.fs
        # self.chunk = self.fs // 10
        # self.audio_device_dll = ctypes.CDLL("../build/xmos-device/libaudio-device-py.dylib")
        self.audio_device_dll = ctypes.CDLL("libaudio-device-py.dylib")
        
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
        self.info = None
        self.mutex = threading.Lock()
    
    def scan(self):
        string_data = bytes(500)
        self.audio_device_dll.ScanAllDevices(string_data)
        self.info = string_data.split(b'|')
        num_devices = int.from_bytes(self.info[0], byteorder='little', signed=True)
        # print(num_devices)
        string = [num_devices]
        
        j = 1
        for i in range(num_devices):
            name = self.info[j].decode()
            string.append(name)
            j += 1
            chans = int.from_bytes(self.info[j], byteorder='little', signed=True)
            string.append(chans)
            j += 1
        return string
    
    def start(self, filename, device_name, num_chan):
        if self.RecordingFlag :
            return
        self.ws = ASRBaseClient(url = self.websockethost, app_id = V_APP_ID, token = self.auth_token, sample_rate = self.fs, 
                                model_type = MODEL_ASR_POWER, func = self.callback, args = self.callback_args)
        py_filename = filename[0:-4] + "-py.wav"
        wf = wave.open(py_filename, 'wb')
        wf.setsampwidth(2)
        wf.setframerate(self.fs)
        self.RecordingFlag = True
        self.ws.connect()
        
        if not device_name:
            device_name = "Microphone"
        print(device_name)
        # self.audio_device_dll.ScanAllDevices()
        max_num_channel = num_chan
        self.audio_device_dll.StartRecording(filename.encode(), device_name.encode())
        wf.setnchannels(1)
        # audio_data = np.zeros([self.fs*max_num_channel, 1], dtype = np.short)
        required_samples = int(12800)
        string_data = bytes((required_samples * max_num_channel * 2))
        while True:
            res = self.audio_device_dll.ReadPcm(string_data, required_samples)
            audio_data = np.fromstring(string_data, dtype = np.short)
            audio_data1 = np.reshape(audio_data, (-1, max_num_channel))
            pcm_data = np.sum(audio_data1, axis=-1, dtype=np.short)
            wf.writeframes(pcm_data.tostring())
            pcm_data1 = np.fromstring(pcm_data.tostring(), dtype = np.short)
            
            if self.ws._is_closed:
                self.ws.connect()
            self.ws.diy_send_binary(pcm_data1)
            # print(type(pcm_data), type(pcm_data1))
            # th1 = threading.Thread(target = self.ws.diy_send_binary, args=(pcm_data1,))
            # th1.start()
            # if self.mutex.acquire():
            if not self.RecordingFlag:
                break
        wf.close()
        print("recording stop")
        self.audio_device_dll.Stop()
        time.sleep(1)
        self.ws.close()
        self.ws = None
        # self.ws = ASRBaseClient(url = websockethost, app_id = V_APP_ID, token = auth_token, sample_rate = self.fs, 
        #                         model_type = MODEL_ASR_POWER, func = callback, args = callback_args)
    
    def stop(self):
        # if self.mutex.acquire():
        # self.audio_device_dll.Stop()
        self.RecordingFlag = False
            # self.mutex.release()

def callback(result, callback_args):
    print("Online Result:%s"%result)

if __name__ == '__main__':
    stream_asr = ConVoiceStreamAsr(callback)
    data_dir = "./data/"
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    filename = data_dir + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
    print(filename)
    th1 = threading.Thread(target = stream_asr.start, args = (filename,))
    th1.start()
    print("Stop recognizing after 10 seconds")
    time.sleep(10)
    stream_asr.stop()
