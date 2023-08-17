#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtCore import Qt, pyqtSignal,QThread,QUrl
from PyQt5.QtGui import QPixmap, QPainter, QColor,QDesktopServices,QPen
from PyQt5.QtWidgets import QWidget,QAbstractItemView,QTableWidgetItem,QGraphicsDropShadowEffect,QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon,MessageBox,StateToolTip
from app.view.Ui_SafetyInterface import Ui_SafetyInterface
from app.tool.adb import adb
from app.common.translator import Translator
from app.common.runtime import rt
from app.lib.myDialog import MyDialog
from app.common.signal_bus import signalBus,signalKey

# MyDialog is a QWidget's subclass,according to mro,QWidget can omit
class SafetyInterface(MyDialog, Ui_SafetyInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = Translator()
        self.setupUi(self)

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
        self.AppList.setHorizontalHeaderLabels([self.t.safety_app_package_name, self.t.safety_app_apk_path])
        self.AppList.resizeColumnsToContents()
        self.AppList.setColumnWidth(0, 150)
        self.AppList.setColumnWidth(1, 390)
        self.AppList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # hide progress
        self.RefreshProgress.hide()
        self.BackupAExtractProgress.hide()

        # disable button
        self.ButtonEtractAPKFile.setEnabled(False)
        self.ButtonBackupData.setEnabled(False)



    def __connectSignal(self):
        # connect
        self.ButtonRefresh.clicked.connect(self.startT_refreshAPPList)
        self.get_app_list_thread.GA_signal.connect(self.callback_refreshAPPList)
        self.AppList.itemSelectionChanged.connect(self.appItemSelectionChanged)

    def appItemSelectionChanged(self):
        """app item selection changed,get selected app info"""
        select = self.AppList.selectedItems()
        select_app = {}
        select_length = len(select)/2
        for i in range(int(select_length)):
            select_app[select[i*2].text()] = select[i*2+1].text()

        if select_app:
            self.ButtonEtractAPKFile.setEnabled(True)
            self.ButtonBackupData.setEnabled(True)
        else:
            self.ButtonEtractAPKFile.setEnabled(False)
            self.ButtonBackupData.setEnabled(False)

        #print(select_app)









    def startT_refreshAPPList(self):
        """ start thread to refresh app list """
        #取消选择
        self.AppList.clearSelection()

        if not rt.DEVICE_ID:
            res = self.showMessageDialog(self.t.error_title, self.t.error_no_device)
            if res:
                # turn to connect interface
                signalBus.switch_page.emit(rt.page_dict['connect'])
            return
        self.ButtonEtractAPKFile.setEnabled(False)
        self.ButtonBackupData.setEnabled(False)
        self.ButtonRefresh.setEnabled(False)
        self.RefreshProgress.stop()
        self.RefreshProgress.start()
        self.RefreshProgress.show()
        self.get_app_list_thread.start()

    def callback_refreshAPPList(self,res):
        """callback of refresh app list"""

        status = res.get('status')
        # clear AppList
        self.AppList.clearContents()
        self.AppList.setRowCount(0)

        if status == signalKey.SUCCESS:
            for i in res['info']:
                self.AppList.insertRow(0)
                self.AppList.setItem(0, 0, QTableWidgetItem(i))
                self.AppList.setItem(0, 1, QTableWidgetItem(res['info'][i]))
            self.RefreshProgress.hide()
            self.ButtonRefresh.setEnabled(True)
        elif status == signalKey.ERROR:
            self.RefreshProgress.hide()
            self.ButtonRefresh.setEnabled(True)
            error = res.get('error')
            self.showMessageDialog(self.t.error_title, error)



class GetApps(QThread):
    GA_signal = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.GA_signal.emit(adb.getApps())
        #adb.exe: no devices/emulators found






