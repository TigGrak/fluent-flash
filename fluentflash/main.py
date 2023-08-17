#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,sys
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator,Theme,setTheme

from app.common.config import cfg
from app.view.main_window import MainWindow
import app.assets.assets_rc

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)



# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()

galleryTranslator.load(locale, "gallery", ".", ":/i18n/i18n/")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
setTheme(Theme.AUTO)
w = MainWindow()
w.show()

app.exec_()