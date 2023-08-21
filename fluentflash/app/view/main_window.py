#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from qfluentwidgets import SplitFluentWindow, FluentIcon, SplitTitleBar, NavigationItemPosition, NavigationPushButton, \
    MessageBox
from app.view.connect_interface import ConnectInterface
from app.view.safety_interface import SafetyInterface
from app.common.config import cfg
from app.common.runtime import rt
from app.common.signal_bus import signalBus
from app.common.translator import Translator


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        self.t = Translator()
        self.__initWindow()
        self.__initSubPage()
        self.__initNavigation()
        self.__connectSignal()

    def __initSubPage(self):
        """init sub page"""
        # creat sub page
        self.connectInterface = ConnectInterface(self)
        self.safetyInterface = SafetyInterface(self)
        page_dict = {"connect": self.connectInterface, "safety": self.safetyInterface}
        rt.savePageDict(page_dict)

    def __initWindow(self):
        """init window"""
        # set new title bar
        self.my_title_bar = NoMaxMinButtonTitleBar(self)
        self.setTitleBar(self.my_title_bar)
        self.my_title_bar.setTitle(cfg.appDisplayName)
        # bug fix: title not show when expand sidebar
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

        # window size
        self.resize(960, 800)
        self.setResizeEnabled(False)

    def __initNavigation(self):
        """init navigation interface"""

        self.addSubInterface(self.connectInterface, FluentIcon.CONNECT, self.t.connect_interface_title)
        self.addSubInterface(self.safetyInterface, FluentIcon.VPN, self.t.safety_interface_title)

        self.navigationInterface.addWidget(
            routeKey='stop_exec_cmd',
            widget=NavigationPushButton(icon=FluentIcon.POWER_BUTTON,
                                        text=self.t.navigation_button_stop_command,
                                        isSelectable=False),
            onClick=lambda: self.stopCommand(),
            position=NavigationItemPosition.BOTTOM.BOTTOM,
            tooltip=self.t.navigation_button_stop_command
        )

        self.navigationInterface.widget('stop_exec_cmd').setEnabled(False)

    def __connectSignal(self):
        """connect signal and"""
        signalBus.switch_page.connect(lambda page: self.__switchPage(page))
        signalBus.runtime_change.connect(lambda runtime: self.callback_runtimeChange(runtime))

    def __switchPage(self, page):
        """switch page"""
        self.switchTo(page)

    def callback_runtimeChange(self, runtime):
        """callback runtime change"""

        name = runtime.get('name')
        value = runtime.get('value')
        if name == 'run_cmd_process':
            if value is None:
                # disable stop command button
                self.navigationInterface.widget('stop_exec_cmd').setEnabled(False)
            else:
                # enable stop command button
                self.navigationInterface.widget('stop_exec_cmd').setEnabled(True)

    def stopCommand(self):
        """stop command"""
        w = MessageBox(
            self.t.risk_warning,
            self.t.stop_command_warning,
            self
        )
        if w.exec():
            signalBus.stop_exec_cmd.emit()


class NoMaxMinButtonTitleBar(SplitTitleBar):
    """ Rewrite the SplitTitleBar class and remove maxBtn """

    def __init__(self, parent):
        super().__init__(parent)
        self.maxBtn.deleteLater()
        self._isDoubleClickEnabled = False
