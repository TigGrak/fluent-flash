#!/usr/bin/env python
# -*- coding:utf-8 -*-

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
