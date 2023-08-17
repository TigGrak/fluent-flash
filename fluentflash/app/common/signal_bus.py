#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal

class SignalBus(QObject):
    """ Signal bus """
    switch_page = pyqtSignal(object)
    runtime_change = pyqtSignal(dict)
    refresh_device = pyqtSignal()

class SignalKey():
    """ Signal key """
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    ERROR = 'ERROR'
    NOT_FOUND = 'NOT_FOUND'
    FOUND = 'FOUND'

signalBus = SignalBus()
signalKey = SignalKey()