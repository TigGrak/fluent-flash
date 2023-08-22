#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QPixmap, QPainter, QColor, QDesktopServices, QPen
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QTableWidgetItem, QGraphicsDropShadowEffect, QVBoxLayout, \
    QHBoxLayout
from qfluentwidgets import FluentIcon, MessageBox, StateToolTip
from app.view.Ui_SafetyInterface import Ui_SafetyInterface
from app.tool.adb import adb
from app.common.translator import Translator
from app.common.config import cfg
from app.common.signal_bus import signalBus, signalKey
from app.common.public import Check


# MyDialog is a QWidget's subclass,according to mro,QWidget can omit
class SafetyInterface(Check, Ui_SafetyInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = Translator()
        self.setupUi(self)

        self.apps_info = {}

        self.get_app_list_thread = GetApps()

        self.__initUI()
        self.__connectSignal()

    def __initUI(self):
        # scroll area transparent bg,no border
        self.ScrollArea.setStyleSheet("background-color:transparent;border:none;")

        # AppList style
        self.AppList.setWordWrap(True)
        self.AppList.setColumnCount(2)
        self.AppList.verticalHeader().hide()
        self.AppList.setHorizontalHeaderLabels([self.t.safety_app_name, self.t.safety_app_package_name])
        self.AppList.resizeColumnsToContents()
        self.AppList.setColumnWidth(0, 150)
        self.AppList.setColumnWidth(1, 390)
        self.AppList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # app info bar
        self.ButtonUninstall.setEnabled(False)
        self.ButtonDisable.setEnabled(False)
        self.ButtonEnable.setEnabled(False)
        self.SelectQuantity.setText(str(0))
        self.InfoBadge.setText(self.t.safety_app_type)


        # hide progress
        self.__setProgressVisible(False)

        # disable button
        self.__setAPKButtonEnable(False)

    def __connectSignal(self):
        # connect
        self.ButtonRefresh.clicked.connect(lambda: self.startT_refreshAPPList())
        self.AppList.itemSelectionChanged.connect(lambda: self.appItemSelectionChanged())
        self.get_app_list_thread.GA_signal.connect(lambda app_info: self.callback_addAppListFinished(app_info))
        signalBus.refresh_device_app_list.connect(lambda app_info: self.callback_addAppList(app_info))


    def __setAPKButtonEnable(self, state):
        self.ButtonEtractAPKFile.setEnabled(state)
        self.ButtonBackupData.setEnabled(state)


    def __setProgressVisible(self, state, reboot=True):

        self.BackupAExtractProgress.setVisible(state)
        if reboot:
            self.BackupAExtractProgress.setValue(0)

    def appItemSelectionChanged(self):
        """app item selection changed,get selected app info"""
        select = self.AppList.selectedItems()
        select_length = len(select) / 2
        select_app = {
            select[i * 2].text(): select[i * 2 + 1].text()
            for i in range(int(select_length))
        }
        print(self.apps_info)
        self.__setAPKButtonEnable(bool(select_app))
        self.SelectQuantity.setText(str(int(select_length)))
        if select_length > 0:
            first_app_name = list(select_app.keys())[0]
            first_app_package_name = list(select_app.values())[0]
            first_app_enable = self.apps_info[first_app_package_name]['enable']
            first_app_type = self.apps_info[first_app_package_name]['type']

            more_text = '...' if select_length > 1 else ''
            self.InfoBadge.setText('...' if select_length > 1 else first_app_type)
            self.APPNameLabel.setText(first_app_name + more_text)
            self.APPPackageNameLabel.setText(first_app_package_name + more_text)

            if select_length == 1:
                self.ButtonUninstall.setEnabled(True)
                self.ButtonEnable.setEnabled(not first_app_enable)
                self.ButtonDisable.setEnabled(first_app_enable)
            else:
                self.ButtonUninstall.setEnabled(False)
                self.ButtonEnable.setEnabled(False)
                self.ButtonDisable.setEnabled(False)
        else:
            self.InfoBadge.setText(self.t.safety_app_type)
            self.APPNameLabel.setText(self.t.NO_DATA)
            self.APPPackageNameLabel.setText(self.t.NO_DATA)
            self.ButtonUninstall.setEnabled(False)
            self.ButtonDisable.setEnabled(False)
            self.ButtonEnable.setEnabled(False)







        print(select_app)

    @Check.checkRunCmd(check_device=True)
    def startT_refreshAPPList(self):
        """ start thread to refresh app list """
        # disable app list selection
        self.AppList.clearSelection()
        self.AppList.setDisabled(True)

        #clear app list
        self.AppList.setRowCount(0)



        self.__setAPKButtonEnable(False)
        self.__setProgressVisible(True)
        self.ButtonRefresh.setEnabled(False)
        self.get_app_list_thread.start()


    def callback_addAppList(self, app_info):
        # {'status':'','info':{},'error':''}
        status = app_info.get('status')
        if status == signalKey.ERROR:
            return
        info = app_info['info']
        if status == signalKey.SET_PROGRESS:
            self.BackupAExtractProgress.setValue(info)
        elif status == signalKey.SUCCESS:
            self.addAppInfo(info)

    def callback_addAppListFinished(self, app_info):
        """finish add app list"""
        self.apps_info = app_info.get('info')
        self.AppList.setDisabled(False)
        self.__setProgressVisible(False)
        self.ButtonRefresh.setEnabled(True)
        if app_info.get('status') == signalKey.ERROR:
            print(111)
            # clear App List
            self.AppList.setRowCount(0)
            self.apps_info = {}
            self.showMessageDialog(self.t.error_title, app_info.get('error'))
            return


    def addAppInfo(self, info):
        key = list(info.keys())[0]
        value = info[key]
        lang = cfg.language.value.value.name().replace('_', '-')
        name = value['name'].get(lang)
        if name is None:
            name = value['name'].get('all')
        self.AppList.insertRow(0)
        self.AppList.setItem(0, 0, QTableWidgetItem(name))
        self.AppList.setItem(0, 1, QTableWidgetItem(key))



class GetApps(QThread):
    GA_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        # push file
        res = adb.push(cfg.aaptPath.value, f'{cfg.cachePath}/aapt')
        if res['status'] == signalKey.ERROR:
            self.GA_signal.emit(res)
            return
        self.GA_signal.emit(adb.getApps())
