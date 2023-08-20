#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Path: app\view\connect_interface.py
# connect ui and backend
# TIGGRAK


from PyQt5.QtCore import pyqtSignal, QThread, QPropertyAnimation,QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from app.view.Ui_ConnectInterface import Ui_ConnectInterface
from qfluentwidgets import FluentIcon, StateToolTip
from app.tool.adb import adb
from app.common.translator import Translator
from app.common.runtime import rt
from app.lib.myDialog import MyDialog
from app.common.signal_bus import signalKey, signalBus


# MyDialog is a QWidget's subclass,according to mro,QWidget can omit
class ConnectInterface(MyDialog, Ui_ConnectInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.t = Translator()
        self.setupUi(self)

        # predefine
        # adb get device info
        self.get_device_info_thread = None
        self.check_device_thread = None
        self.get_ROOT_thread = None

        self.get_ROOT_state_tool_tip = None

        self.__initUI()
        self.__connectSignal()

    def __initUI(self):
        # set ui
        self.ConnectPrimaryToolButton.setIcon(FluentIcon.UPDATE)
        self.setShadowEffect(self.InfoCard1)
        self.setShadowEffect(self.InfoCard2)
        self.setShadowEffect(self.InfoCard3)
        self.setShadowEffect(self.InfoCard4)
        self.setShadowEffect(self.InfoCard5)
        self.setShadowEffect(self.InfoCard6)

        # hide GetDeviceInfoIndeterminateProgressBar and GetROOTPermissions
        self.GetDeviceInfoIndeterminateProgressBar.hide()
        self.GetROOTPermissions.hide()

    def __connectSignal(self):
        # connect GetROOTPermissions checkbox
        self.GetROOTPermissions.clicked.connect(lambda: self.ifGetROOTPermissionsChecked())
        # connect find device button
        self.ConnectPrimaryToolButton.clicked.connect(lambda: self.startT_findDevice())
        # connect refresh device signal
        signalBus.refresh_device.connect(lambda: self.callback_refreshDevice())

    def setShadowEffect(self, card: QWidget):
        """from clock demo"""
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)


    def onGetROOT(self, disable=False):
        """set state tool tip when getting root"""

        if self.get_ROOT_state_tool_tip:
            if disable:
                self.get_ROOT_state_tool_tip.setContent(
                    self.t.stop_operation_success)
            else:
                self.get_ROOT_state_tool_tip.setContent(
                    self.t.getting_root_success)
            self.get_ROOT_state_tool_tip.setState(True)
            self.get_ROOT_state_tool_tip = None
        elif not disable:
            self.get_ROOT_state_tool_tip = StateToolTip(
                self.t.getting_root_title, self.t.getting_root_content, self.window())
            self.get_ROOT_state_tool_tip.move(self.get_ROOT_state_tool_tip.getSuitablePos())
            self.get_ROOT_state_tool_tip.show()

    def ifGetROOTPermissionsChecked(self):
        """connected by GetROOTPermissions checkbox, if checked, start getting root"""
        if self.GetROOTPermissions.isChecked():
            self.startT_gettingROOT()

        else:
            self.onGetROOT(disable=True)
            rt.setRoot(False)

    def callback_getDeviceInfo(self, res):
        """callback function,update device info ui"""


        if res.get('status') != signalKey.SUCCESS:
            self.showMessageDialog(self.t.error_title, res.get('error'))
            rt.setDeviceId('')
            return

        device_info = res.get('info')

        self.InfoText1.setText(
            f"{device_info['device_name']}\n{device_info['device_model']}\n{device_info['device_memory']}\\{device_info['device_storage']}\n{device_info['device_manufacture']}")
        self.InfoText1_2.setText(
            f"Android {device_info['device_android_version']}\n{device_info['ui_version']}\n{device_info['ui_build']}")
        self.InfoText1_3.setText(f"{device_info['device_kernel_version']}")

        # set \n at 22
        device_baseband_version1 = device_info['device_baseband_version'][:22]
        device_baseband_version2 = device_info['device_baseband_version'][22:]
        self.InfoText1_4.setText(f"{device_baseband_version1}\n{device_baseband_version2}")

        self.InfoText1_5.setText(f"{device_info['device_security_patch_date']}")
        self.InfoText1_6.setText(
            f"{device_info['device_connect_type']}\n{device_info['device_id']}\n{device_info['adb_version']}\n{device_info['windows_version']}")

        self.GetROOTPermissions.show()
        self.GetDeviceInfoIndeterminateProgressBar.hide()
        self.ConnectPrimaryToolButton.setEnabled(True)


    def callback_findDevice(self, device_dict):
        """callback function,update find device ui"""



        if device_dict.get('status') == signalKey.FOUND:
            self.startT_getDeviceInfo(device_dict)
            return
            # device_info = adb.getDeviceInfo(device_id)
        elif device_dict.get('status') == signalKey.NOT_FOUND:
            self.showMessageDialog(self.t.error_title, self.t.error_device_adb_not_found)
        elif device_dict.get('status') == signalKey.ERROR:
            self.showMessageDialog(self.t.error_title, device_dict.get('error'))
        self.GetDeviceInfoIndeterminateProgressBar.hide()
        self.ConnectPrimaryToolButton.setEnabled(True)
        rt.setDeviceId('')







    def startT_getDeviceInfo(self, device_dict):
        # TODO
        device_id = list(device_dict['info'].keys())[0]
        rt.setDeviceId(device_id)
        # if device_id is a ip ,add to IPEditableComboBox
        if device_id.find(':') != -1 and self.IPEditableComboBox.findText(device_id) == -1:
            self.IPEditableComboBox.addItem(device_id)

        self.get_device_info_thread = GetDeviceInfoThread()
        self.get_device_info_thread.GDI_signal.connect(lambda res: self.callback_getDeviceInfo(res))
        self.get_device_info_thread.start()

    def callback_getROOT(self, res: bool):
        """callback function,update get root ui"""
        if res:
            self.onGetROOT()
            rt.setRoot(True)
        else:
            self.onGetROOT(disable=True)
            rt.setRoot(False)
            # if checkbox is checked
            if self.GetROOTPermissions.isChecked():
                self.GetROOTPermissions.setChecked(False)
                self.showMessageDialog(self.t.error_title, self.t.error_get_superuser_failed)

    def callback_refreshDevice(self):
        rt.setRoot(False)
        # init ui
        self.InfoText1.setText(self.t.NO_DATA)
        self.InfoText1_2.setText(self.t.NO_DATA)
        self.InfoText1_3.setText(self.t.NO_DATA)
        self.InfoText1_4.setText(self.t.NO_DATA)
        self.InfoText1_5.setText(self.t.NO_DATA)
        self.InfoText1_6.setText(self.t.NO_DATA)

        self.ConnectPrimaryToolButton.setEnabled(False)
        self.GetROOTPermissions.setChecked(False)
        self.GetROOTPermissions.hide()
        self.GetDeviceInfoIndeterminateProgressBar.show()
        self.GetDeviceInfoIndeterminateProgressBar.stop()
        self.GetDeviceInfoIndeterminateProgressBar.start()

    def startT_findDevice(self):
        """start thread to find device"""

        self.onGetROOT(disable=True)
        signalBus.refresh_device.emit()
        # get IPEditableComboBox value
        host = self.IPEditableComboBox.currentText()

        host = None if host == '' else host
        self.check_device_thread = FindDeviceThread(host)
        self.check_device_thread.FDT_signal.connect(lambda device_dict: self.callback_findDevice(device_dict))

        # start thread
        self.check_device_thread.start()

    def startT_gettingROOT(self):
        """start thread to get root"""
        if self.showMessageDialog(
                self.t.risk_warning, self.t.get_ROOT_permissions_tips
        ):
            self.onGetROOT()
            self.get_ROOT_thread = GettingROOTThread()
            self.get_ROOT_thread.GRT_signal.connect(lambda root_res: self.callback_getROOT(root_res))
            self.get_ROOT_thread.start()
        else:
            self.GetROOTPermissions.setChecked(False)
            return


"""QThread for find device"""


class FindDeviceThread(QThread):
    FDT_signal = pyqtSignal(dict)

    def __init__(self, host=None):
        super().__init__()
        self.device_info = {}
        self.host = host

    def run(self):
        self.device_info = adb.checkDevice(host=self.host)
        self.FDT_signal.emit(self.device_info)


"""QThread for get device info"""""


class GetDeviceInfoThread(QThread):
    GDI_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.device_info = {}

    def run(self):
        self.device_info = adb.getDeviceInfo()
        self.GDI_signal.emit(self.device_info)


"""QThread for try getting root"""


class GettingROOTThread(QThread):
    GRT_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        get_root_status = adb.checkSU()
        self.GRT_signal.emit(get_root_status)
