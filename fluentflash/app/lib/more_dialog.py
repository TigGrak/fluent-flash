# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,QWidget


from PyQt5.QtCore import Qt,QRect

from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qfluentwidgets.components.widgets.scroll_area import SingleDirectionScrollArea
from qfluentwidgets import ComboBox,ColorDialog,PrimaryPushButton

class chooseDialog(MaskDialogBase, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))


        self.choose_widget = ComboBox(self)
        self.choose_widget.setObjectName("choose_widget")
        self.choose_widget.setGeometry(QRect(400, 400, 200, 30))

        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Resize:
                self._adjustText()

        return super().eventFilter(obj, e)

class inputDialog(MaskDialogBase):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self.scrollArea = SingleDirectionScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)
        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton(self.tr('OK'), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr('Cancel'), self.buttonGroup)





