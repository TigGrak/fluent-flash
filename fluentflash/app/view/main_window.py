#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QHBoxLayout,QLabel
from PyQt5.QtGui import QIcon
from qfluentwidgets import SplitFluentWindow,FluentIcon,setTheme,Theme,FluentStyleSheet,SplitTitleBar
from qframelesswindow import TitleBar


# noinspection PyUnresolvedReferences
from app.view.connect_interface import ConnectInterface
# noinspection PyUnresolvedReferences
from app.view.safety_interface import SafetyInterface
# noinspection PyUnresolvedReferences
from app.common.config import cfg


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        #set new title bar

        self.my_title_bar = NoMaxMinButtonTitleBar(self)
        self.setTitleBar(self.my_title_bar)
        self.my_title_bar.setTitle(cfg.appDisplayName)

        #bug fix: title not show when expand sidebar
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

        # window size
        self.resize(960, 800)
        self.setResizeEnabled(False)

        # creat and connect sidebar menu
        self.connectInterface = ConnectInterface(self)
        self.safetyInterface = SafetyInterface(self)
        self.addSubInterface(self.connectInterface,FluentIcon.CONNECT,"Connect")
        self.addSubInterface(self.safetyInterface, FluentIcon.VPN, "Safety")




class NoMaxMinButtonTitleBar(SplitTitleBar):
    """ Rewrite the SplitTitleBar class and remove maxBtn """
    def __init__(self, parent):
        super().__init__(parent)
        self.maxBtn.deleteLater()
        self._isDoubleClickEnabled = False


