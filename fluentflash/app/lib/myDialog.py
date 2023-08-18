#!/usr/bin/env python
# -*- coding:utf-8 -*-

from qfluentwidgets import MessageBox
from app.lib.more_dialog import chooseDialog
from PyQt5.QtWidgets import QWidget


class MyDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def showMessageDialog(self, title, content):
        """show message dialog"""
        w = MessageBox(title, content, self.window())
        return bool(w.exec())

    def showChooseDialog(self, title, content):
        # TODO:BUG
        """choose dialog coding by myself,BUG"""
        w = chooseDialog(title, content, self.window())
        return bool(w.exec())
