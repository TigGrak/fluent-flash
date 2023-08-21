#!/usr/bin/env python
# -*- coding:utf-8 -*-

import signal
from functools import wraps
from app.common.signal_bus import signalBus


class Runtime():
    def __init__(self):
        super().__init__()
        self.ROOT = False
        self.DEVICE_ID = ''
        self.DEVICE_INFO = {}
        self.page_dict = {}
        self.run_cmd_process = None
        self.run_cmd_process_status = True

        self.__connectSiganl()

    def __connectSiganl(self):
        """connect signal"""
        signalBus.stop_exec_cmd.connect(lambda: self.callback_stopExecCmd())

    def callback_stopExecCmd(self):
        if self.run_cmd_process is not None:
            self.run_cmd_process.send_signal(signal.CTRL_BREAK_EVENT)
            self.setRunCmdProcessStatus(False)

    """Send a message to the UI saying "时代变啦" every time an attribute is modified."""

    def sendSignal(attr_name):
        def wrapper(func):
            @wraps(func)
            def inner(self, *args, **kwargs):
                if getattr(self, attr_name) != args[0]:
                    signalBus.runtime_change.emit({'name': attr_name, 'value': args[0]})
                return func(self, *args, **kwargs)

            return inner

        return wrapper
        # self.RT_signal.emit({name: value})

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

    def savePageDict(self, page_dict):
        """navigation page dict"""
        self.page_dict = page_dict

    def setRunCmdProcessStatus(self, process_status):
        """set run cmd process status"""
        self.run_cmd_process_status = process_status

    @sendSignal('run_cmd_process')
    def setRunCmdProcess(self, process):
        """set run cmd process"""
        self.run_cmd_process = process


rt = Runtime()
