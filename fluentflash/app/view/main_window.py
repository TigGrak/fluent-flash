#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget,QHBoxLayout,QLabel
from PyQt5.QtGui import QIcon
from qfluentwidgets import SplitFluentWindow,FluentIcon,setTheme,Theme,FluentStyleSheet,SplitTitleBar


from app.view.connect_interface import ConnectInterface
from app.view.safety_interface import SafetyInterface
from app.common.config import cfg
from app.common.runtime import rt
from app.common.signal_bus import signalBus


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

        page_dict = {"connect":self.connectInterface,"safety":self.safetyInterface}
        rt.savePageDict(page_dict)



        self.addSubInterface(self.connectInterface,FluentIcon.CONNECT,"Connect")
        self.addSubInterface(self.safetyInterface, FluentIcon.VPN, "Safety")

        self.__connectSignal()




    def __connectSignal(self):
        """connect signal and"""
        signalBus.switch_page.connect(self.__switchPage)

    def __switchPage(self,page):
        self.switchTo(page)





class NoMaxMinButtonTitleBar(SplitTitleBar):
    """ Rewrite the SplitTitleBar class and remove maxBtn """
    def __init__(self, parent):
        super().__init__(parent)
        self.maxBtn.deleteLater()
        self._isDoubleClickEnabled = False


