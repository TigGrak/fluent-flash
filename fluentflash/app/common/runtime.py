#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtCore import pyqtSignal,QObject
from functools import wraps






class Runtime(QObject):
    RT_signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.ROOT = False
        self.DEVICE_ID = ''
        self.DEVICE_INFO = {}

    """Send a message to the UI saying "时代变啦" every time an attribute is modified."""
    def sendSignal(attr_name):
        def wrapper(func):
            @wraps(func)
            def inner(self,*args,**kwargs):
                if getattr(self,attr_name) != args[0]:
                    self.RT_signal.emit({'name': attr_name,'value':args[0]})
                return func(self,*args,**kwargs)
            return inner
        return wrapper
        #self.RT_signal.emit({name: value})

    """change root status"""
    @sendSignal('ROOT')
    def setRoot(self, root: bool):
        self.ROOT = root

    """change device id"""
    @sendSignal('DEVICE_ID')
    def setDeviceId(self, device_id: str):
        self.DEVICE_ID = device_id

    """change device info"""
    @sendSignal('DEVICE_INFO')
    def setDeviceInfo(self, device_info: dict):
        self.DEVICE_INFO = device_info






rt = Runtime()

