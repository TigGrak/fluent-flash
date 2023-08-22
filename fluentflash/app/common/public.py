#!/usr/bin/env python
# -*- coding:utf-8 -*-

from functools import wraps
from app.lib.myDialog import MyDialog
from app.common.runtime import rt
from app.common.signal_bus import signalBus
from app.common.translator import Translator


class Check(MyDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.t = Translator()

    def checkDevice(self):
        if not rt.DEVICE_ID and self.showMessageDialog(
                self.t.error_title, self.t.error_no_device
        ):
            signalBus.switch_page.emit(rt.page_dict['connect'])
        return bool(rt.DEVICE_ID)

    def checkRunCmd(check_device=True):
        """check run cmd status"""

        def wrapper(func):
            @wraps(func)
            def inner(self, *args, **kwargs):
                if rt.run_cmd_process is not None:
                    self.showMessageDialog(
                        self.t.error_title, self.t.command_running
                    )

                elif check_device and (not rt.DEVICE_ID) and self.showMessageDialog(self.t.error_title,self.t.error_no_device):
                    signalBus.switch_page.emit(rt.page_dict['connect'])

                else:
                    func(self, *args, **kwargs)

            return inner

        return wrapper

    def checkRunCmd_bool(self, check_device=True):
        if rt.run_cmd_process is not None:
            self.showMessageDialog(
                self.t.error_title, self.t.command_running
            )
            return False

        elif check_device and (not rt.DEVICE_ID):
            if self.showMessageDialog(self.t.error_title, self.t.error_no_device):
                signalBus.switch_page.emit(rt.page_dict['connect'])
            return False
        else:
            return True
