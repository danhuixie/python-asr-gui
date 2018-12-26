#!/usr/bin/env python

from __future__ import absolute_import, unicode_literals, division, print_function
from asr_demo import run_asr
import sys, time
import os
import wx
import threading
from asr_stream import *
from array_stream import *
from convoice_stream import *

def asr_callback(t1, t2):
    wx.CallAfter(t2.logger.Clear)
    status_info = t2.status_info.GetValue()
    str_list = status_info.split(" ")
    tag_name = str_list[-1] + " :"
    wx.CallAfter(print, tag_name, t1)
    # new_result = t1.lstrip(t2.result_string)
    # t2.result_string = t1
    # wx.CallAfter(print, new_result, end="")
    
    
def gui_run_asr(File_Name, callback, gui):
    gui.send_button.SetLabel("Sending")
    text = run_asr(File_Name, callback, gui)
    status_info = gui.status_info.GetValue()
    str_list = status_info.split(" ")
    tag_name = str_list[-1]
    wx.CallAfter(gui.status_info.Clear)
    wx.CallAfter(gui.status_info.AppendText, tag_name)
    gui.send_button.SetLabel("Send")

def stream_asr_callback(result, gui):
    wx.CallAfter(gui.logger.Clear)
    wx.CallAfter(print, "Online Result: " + result)

class MainWindow(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,500))
        
        # self.CreateStatusBar()
        # self.result_string="Online Result"
        
        #Setting up the menu
        filemenu = wx.Menu()
        menuItem = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate the program")
        # filemenu.AppendSeparator()
        
        #Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        
        #Events
        self.Bind(wx.EVT_MENU, self.OnAbout, menuItem)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        #Sizer1
        self.logger = wx.TextCtrl(self, wx.ID_ANY, size=(700, 500), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)
        sys.stdout = self.logger;
        
        #Sizer2
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.button1 = wx.Button(self, -1, "PC Record")
        self.button2 = wx.Button(self, -1, "Array Record")
        
        # self.soundcard_list.SetString(0, "this is test A")
        # self.soundcard_list.SetString(1, "A is the test")
        # self.soundcard_list.Clear()
        # self.soundcard_list.AppendItems(['a', 'b', 'c', 'e', 'f'])
        # self.soundcard_list.Destroy()
        # self.soundcard_list = wx.Choice(self, id=wx.ID_ANY, choices=['a', 'b', 'c', 'd', 'e', 'f'])
        
        self.sizer2.Add(self.button1, 1, wx.EXPAND)
        self.sizer2.Add(self.button2, 1, wx.EXPAND)
        
        self.Bind(wx.EVT_BUTTON, self.OnClick1, self.button1)
        self.Bind(wx.EVT_BUTTON, self.OnClick2, self.button2)
        
        
        #Sizer SoundCard
        self.usb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.soundcard_button = wx.Button(self, -1, "SoundCard Record")
        self.soundcard_button.Disable()
        self.scan_botton = wx.Button(self, -1, "Scan")
        self.soundcard_list = wx.Choice(self, id=wx.ID_ANY, choices=['Built-in Microphone'])
        self.channel_list = wx.Choice(self, id=wx.ID_ANY, choices=['1'])
        usb_info1 = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        usb_info1.AppendText("Microphone:")
        self.usb_sizer.Add(usb_info1, 1, wx.EXPAND)
        self.usb_sizer.Add(self.soundcard_list, 1, wx.EXPAND)
        
        usb_info2 = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        usb_info2.AppendText("Channel:")
        self.usb_sizer.Add(usb_info2, 1, wx.EXPAND)
        self.usb_sizer.Add(self.channel_list, 1, wx.EXPAND)
        self.usb_sizer.Add(self.scan_botton, 1, wx.EXPAND)
        self.usb_sizer.Add(self.soundcard_button, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnClickSoundCard, self.soundcard_button)
        self.Bind(wx.EVT_BUTTON, self.OnClickScan, self.scan_botton)
        self.Bind(wx.EVT_CHOICE, self.OnSelectDevice, self.soundcard_list)
        
        #Sizer3
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        wave_name = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        wave_name.AppendText("File name:")
        self.file_abs = wx.TextCtrl(self, wx.ID_ANY)
        self.result_string=""
        self.file_abs.AppendText("data/20181219231916-py.wav")
        self.send_button = wx.Button(self, -1, "Send")
        self.Bind(wx.EVT_BUTTON, self.OnClick3, self.send_button)
        self.sizer3.Add(wave_name, 0, wx.ALL)
        self.sizer3.Add(self.file_abs, 5, wx.EXPAND)
        self.sizer3.Add(self.send_button, 1, wx.EXPAND | wx.ALL | wx.ALIGN_TOP)
        
        #Sizer4
        self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        self.status_info = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        self.current_status = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        self.current_status.AppendText("Current Status:")
        self.sizer4.Add(self.current_status, 1, wx.EXPAND)
        self.sizer4.Add(self.status_info, 5, wx.EXPAND)
        
        #Whole Box Size
        spacer = 1
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.logger, 1, wx.EXPAND)
        self.sizer.AddSpacer(spacer)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        self.sizer.AddSpacer(spacer)
        self.sizer.Add(self.usb_sizer, 0, wx.EXPAND)
        self.sizer.AddSpacer(spacer)
        self.sizer.Add(self.sizer3, 0, wx.EXPAND)
        self.sizer.AddSpacer(spacer)
        self.sizer.Add(self.sizer4, 0, wx.EXPAND)
        
        wav_dir = "./data/"
        if not os.path.isdir(wav_dir):
            os.makedirs(wav_dir)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show(True)

        self.stream_asr = RealTimeStreamAsr(callback = stream_asr_callback, callback_args=self)
        self.array_stream_asr = RealTimeArrayStreamAsr(callback = stream_asr_callback, callback_args=self)
        self.soundcard_asr = ConVoiceStreamAsr(callback = stream_asr_callback, callback_args = self)
        self.RecordingFlag = False
        self.filename = None
        self.device_info = [1, "Built-in Microphone", 1]
        self.device_name_list = ["Built-in Microphone"]
        self.device_chan_list = [1]
        
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnExit(self, e):
        self.Close(True)
    
    def OnClick1(self, e):
        try:
            if not self.RecordingFlag:
                self.RecordingFlag = True
                self.filename = "./data/" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
                self.status_info.Clear()
                self.status_info.AppendText("Recognizing %s"%self.filename)
                try:
                    th1 = threading.Thread(target= self.stream_asr.start, args=(self.filename,))
                    th1.start()
                    self.button1.SetLabel("PC Stop")
                except:
                    self.logger.AppendText("Error in starting thread")
            else: 
                self.status_info.Clear()
                self.status_info.AppendText(self.filename)
                th1 = threading.Thread(target= self.stream_asr.stop)
                th1.start()
                self.button1.SetLabel("PC Record")
                self.RecordingFlag = False
        except:
            self.logger.AppendText("Error")

    def OnClick2(self, e):
        try:
            if not self.RecordingFlag:
                self.RecordingFlag = True
                self.filename = "./data/" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
                self.status_info.Clear()
                self.status_info.AppendText("Recognizing %s"%self.filename)
                try:
                    th1 = threading.Thread(target= self.array_stream_asr.start, args=(self.filename,))
                    th1.start()
                    self.button2.SetLabel("Array Stop")
                except:
                    self.logger.AppendText("Error in starting thread")
            else: 
                self.status_info.Clear()
                self.status_info.AppendText(self.filename)
                th1 = threading.Thread(target= self.array_stream_asr.stop)
                th1.start()
                self.button2.SetLabel("Array Record")
                self.RecordingFlag = False
        except:
            self.logger.AppendText("Error")
    
    def OnClick3(self, e):
        try:
            file_name = self.file_abs.GetValue()
            if os.path.isfile(file_name):
                wav_file_list = file_name.split('/')
                self.wav_file = wav_file_list[-1]
                self.status_info.Clear()
                self.status_info.AppendText("Recognizing %s"%self.wav_file)
                self.logger.AppendText("%s:\n"%self.wav_file)
                th1 = threading.Thread(target= gui_run_asr, args=(file_name, asr_callback, self, ));
                th1.start();
            else:
                self.logger.AppendText("Cannot find %s"%file_name)
        except:
            self.logger.AppendText("Error")
    
    def OnClickSoundCard(self, e):
        try:
            if not self.RecordingFlag:
                self.RecordingFlag = True
                self.filename = "./data/" + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + ".wav"
                self.status_info.Clear()
                self.status_info.AppendText("Recognizing %s"%self.filename)
                try:
                    index = self.soundcard_list.GetSelection()
                    dev_nm = self.device_name_list[index]
                    num_chan = self.device_chan_list[index]
                    th1 = threading.Thread(target= self.soundcard_asr.start, args=(self.filename, dev_nm, num_chan))
                    th1.start()
                    self.soundcard_button.SetLabel("SoundCard Stop")
                except:
                    self.logger.AppendText("Error in starting thread")
            else: 
                self.status_info.Clear()
                self.status_info.AppendText(self.filename)
                th1 = threading.Thread(target= self.soundcard_asr.stop)
                th1.start()
                self.soundcard_button.SetLabel("SoundCard Record")
                self.RecordingFlag = False
        except:
            self.logger.AppendText("Error")
            
    def OnClickScan(self, e):
        try:
            self.device_info = self.soundcard_asr.scan()
            self.soundcard_list.Clear()
            self.device_name_list = self.device_info[1 : -1 : 2]
            self.device_chan_list = self.device_info[2 : : 2]
            self.soundcard_list.AppendItems(self.device_name_list)
            self.soundcard_list.SetSelection(0)
            
            # list1 = list(range(1, self.device_chan_list[0] + 1))
            # print(self.device_info)
            # print(self.device_chan_list)
            # range_channel = [str(x) for x in list1]
            # self.channel_list.Clear()
            # self.channel_list.AppendItems(range_channel)
            # self.channel_list.SetSelection(0)
            range_channel = list(str(self.device_chan_list[0]))
            self.channel_list.Clear()
            self.channel_list.AppendItems(range_channel)
            self.channel_list.SetSelection(0)
            self.soundcard_button.Enable()
        except:
            self.logger.AppendText("Error")
    def OnSelectDevice(self, e):
        try:
            index = self.soundcard_list.GetSelection()
            # print(self.device_chan_list)
            # list1 = list(range(1, self.device_chan_list[index] + 1))
            # range_channel = [str(x) for x in list1]
            # self.channel_list.Clear()
            # self.channel_list.AppendItems(range_channel)
            # self.channel_list.SetSelection(0)
            
            range_channel = list(str(self.device_chan_list[index]))
            self.channel_list.Clear()
            self.channel_list.AppendItems(range_channel)
            self.channel_list.SetSelection(0)
        except:
            self.logger.AppendText("Error")
 
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainWindow(None, 'VoiceAI Online Speech Recognition')
    app.MainLoop()
    sys.stdout = sys.__stdout__