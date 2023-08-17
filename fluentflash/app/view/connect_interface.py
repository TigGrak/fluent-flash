#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Path: app\view\connect_interface.py
# connect ui and backend
# TIGGRAK


from PyQt5.QtCore import pyqtSignal,QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget,QGraphicsDropShadowEffect
from app.view.Ui_ConnectInterface import Ui_ConnectInterface
from qfluentwidgets import FluentIcon,MessageBox,StateToolTip
from app.tool.adb import adb
from app.common.translator import Translator
from app.lib.more_dialog import chooseDialog
from app.common.runtime import rt

class ConnectInterface(QWidget, Ui_ConnectInterface):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.t = Translator()
        self.setupUi(self)

        # predefine
        # adb get device info
        self.get_device_info_thread = None
        self.check_device_thread = None
        self.get_ROOT_thread = None

        self.get_ROOT_state_tool_tip = None



        # set ui
        self.ConnectPrimaryToolButton.setIcon(FluentIcon.UPDATE)
        self.setShadowEffect(self.InfoCard1)
        self.setShadowEffect(self.InfoCard2)
        self.setShadowEffect(self.InfoCard3)
        self.setShadowEffect(self.InfoCard4)
        self.setShadowEffect(self.InfoCard5)
        self.setShadowEffect(self.InfoCard6)

        # connect find device button
        self.ConnectPrimaryToolButton.clicked.connect(self.startT_findDevice)

        # hide GetDeviceInfoIndeterminateProgressBar and GetROOTPermissions
        self.GetDeviceInfoIndeterminateProgressBar.hide()
        self.GetROOTPermissions.hide()

        # connect GetROOTPermissions checkbox
        self.GetROOTPermissions.clicked.connect(self.ifGetROOTPermissionsChecked)




    def setShadowEffect(self, card: QWidget):
        """from clock demo"""
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

    def onGetROOT(self,disable=False):
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
        else:
            if not disable:
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

    def showMessageDialog(self,title,content):
        """show message dialog"""
        w = MessageBox(title, content, self.window())
        if w.exec():
            return True
        else:
            return False

    def showChooseDialog(self,title,content):
        #TODO:BUG
        """choose dialog coding by myself,BUG"""
        w = chooseDialog(title, content, self.window())
        if w.exec():
            return True
        else:
            return False

    def callback_getDeviceInfo(self,device_info):
        """callback function,update device info ui"""

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

        self.GetDeviceInfoIndeterminateProgressBar.hide()
        self.GetROOTPermissions.show()
        self.ConnectPrimaryToolButton.setEnabled(True)

    def callback_findDevice(self,device_dict):
        """callback function,update find device ui"""

        if device_dict.get('status') == 'FOUND':

            device_id = list(device_dict['devices'].keys())[0]
            # if device_id is a ip ,add to IPEditableComboBox
            if device_id.find(':') != -1:
                if self.IPEditableComboBox.findText(device_id) == -1:
                    self.IPEditableComboBox.addItem(device_id)

            self.get_device_info_thread = GetDeviceInfoThread(device_id)
            self.get_device_info_thread.GDI_signal.connect(self.callback_getDeviceInfo)
            self.get_device_info_thread.start()
            #device_info = adb.getDeviceInfo(device_id)
        elif device_dict.get('status') == 'NOT_FOUND':
            self.GetDeviceInfoIndeterminateProgressBar.hide()
            self.GetROOTPermissions.hide()
            self.ConnectPrimaryToolButton.setEnabled(True)
            self.showMessageDialog(self.t.error_title, self.t.error_no_device)

    def callback_getROOT(self, res:bool):
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





    def startT_findDevice(self):
        """start thread to find device"""
        self.onGetROOT(disable=True)
        # get IPEditableComboBox value
        host = self.IPEditableComboBox.currentText()
        if host == '':
            host = None

        self.check_device_thread = FindDeviceThread(host)
        self.check_device_thread.FDT_signal.connect(self.callback_findDevice)

        # init ui
        self.ConnectPrimaryToolButton.setEnabled(False)
        self.GetROOTPermissions.setChecked(False)
        self.GetROOTPermissions.hide()
        self.GetDeviceInfoIndeterminateProgressBar.show()
        self.GetDeviceInfoIndeterminateProgressBar.stop()
        self.GetDeviceInfoIndeterminateProgressBar.start()

        # start thread
        self.check_device_thread.start()

    def startT_gettingROOT(self):
        """start thread to get root"""
        res = self.showMessageDialog(self.t.risk_warning, self.t.get_ROOT_permissions_tips)
        if res:
            self.onGetROOT()
            self.get_ROOT_thread = GettingROOTThread()
            self.get_ROOT_thread.GRT_signal.connect(self.callback_getROOT)
            self.get_ROOT_thread.start()
        else:
            self.GetROOTPermissions.setChecked(False)
            return




"""QThread for find device"""
class FindDeviceThread(QThread):
    FDT_signal = pyqtSignal(dict)

    def __init__(self,host=None):
        super().__init__()
        self.device_info = {}
        self.host = host
    def run(self):

        self.device_info = adb.checkDevice(host=self.host)
        self.FDT_signal.emit(self.device_info)



"""QThread for get device info"""""
class GetDeviceInfoThread(QThread):
    GDI_signal = pyqtSignal(dict)

    def __init__(self,device_id):
        super().__init__()
        self.device_info = {}
        self.device_id = device_id
    def run(self):
        self.device_info = adb.getDeviceInfo(self.device_id)
        self.GDI_signal.emit(self.device_info)

"""QThread for try getting root"""
class GettingROOTThread(QThread):
    GRT_signal = pyqtSignal(bool)
    def __init__(self):
        super().__init__()

    def run(self):
        get_root_status = adb.checkSU()
        self.GRT_signal.emit(get_root_status)