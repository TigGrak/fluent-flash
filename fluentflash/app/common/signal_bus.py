#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """
    switch_page = pyqtSignal(object)
    runtime_change = pyqtSignal(dict)
    refresh_device = pyqtSignal()
    check_device = pyqtSignal()
    refresh_device_app_list = pyqtSignal(dict)
    stop_exec_cmd = pyqtSignal()
    extract_apk = pyqtSignal(dict)


class SignalKey():
    """ Signal key """
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    ERROR = 'ERROR'
    NOT_FOUND = 'NOT_FOUND'
    FOUND = 'FOUND'
    ON = 'ON'
    OFF = 'OFF'
    SET_PROGRESS = 'SET_PROGRESS'


signalBus = SignalBus()
signalKey = SignalKey()
