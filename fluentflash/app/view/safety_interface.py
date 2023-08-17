#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtCore import Qt, pyqtSignal,QThread,QUrl
from PyQt5.QtGui import QPixmap, QPainter, QColor,QDesktopServices,QPen
from PyQt5.QtWidgets import QWidget,QGraphicsDropShadowEffect,QVBoxLayout, QHBoxLayout
from app.view.Ui_SafetyInterface import Ui_SafetyInterface
from app.tool.adb import adb
from app.common.translator import Translator
from app.lib.more_dialog import chooseDialog

class SafetyInterface(QWidget, Ui_SafetyInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = Translator()
        self.setupUi(self)
        #scroll area 设置透明,无边框
        self.ScrollArea.setStyleSheet("background-color:transparent;border:none;")

