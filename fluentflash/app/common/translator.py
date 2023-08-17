# coding: utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.connect_interface_title = self.tr('Connect')

        self.risk_warning = self.tr('Risk Warning')
        self.get_ROOT_permissions_tips = self.tr('After obtaining ROOT access, this software will have full control and operation over your device. This could lead to irreversible damage to your device, and the author will not be held responsible for any consequences arising from this. If you believe you are familiar with ROOT-related operations, you may proceed.')
        self.error_title = self.tr('Error')
        self.error_get_superuser_failed = self.tr('Failed to obtain superuser permissions, please check if the device is rooted and allows Shell (com.android.shell) to access superuser requests.')
        self.error_no_device = self.tr('Device not found. Please check if the cable is connected correctly or if the IP address is entered correctly.')
        self.stop_operation_success = self.tr('Operation canceled or permission acquisition failed.')
        self.getting_root_title = 'ROOT'
        self.getting_root_content = self.tr('Attempting to acquire superuser permissions. Please allow the request on your device.')
        self.getting_root_success = self.tr('Superuser permissions obtained successfully. Please use with caution.')