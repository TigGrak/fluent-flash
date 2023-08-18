#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    version = "0.0.1"
    qtVersion = __version__
    appName = "FluentFlash"
    appDisplayName = "FluentFlash"
    appAuthor = "TigGrak"

    cachePath = '/data/local/tmp/fluent_flash'

    ADBPath = ConfigItem('all', 'ADBPath', './app/bin/adb.exe')
    aaptPath = ConfigItem('all', 'aaptPath', './app/bin/device/aapt')
    ifLog = ConfigItem('all', 'ifLog', True)

    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


cfg = Config()
qconfig.load('app/config/config.json', cfg)
cfg.save()
#print(cfg.language.value.value.name())
"""

cfg.set(cfg.aaptPath, './app/bin/device/aapt')
print(cfg.aaptPath)
"""

