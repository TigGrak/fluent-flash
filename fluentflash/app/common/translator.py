# coding: utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.connect_interface_title = self.tr('Connect')
        self.safety_interface_title = self.tr('Safety')

        self.navigation_button_stop_command = self.tr('Stop execution cmd')
        self.stop_command_warning = self.tr(
            'Are you sure you want to forcefully stop the running command? This could potentially lead to software '
            'malfunctions or device damage.')
        self.no_command_running = self.tr('No command is currently running.')
        self.stop_command_success = self.tr('The command has been terminated.')
        self.command_running = self.tr(
            'An operation is currently running. Multiple operations cannot be executed simultaneously.')

        self.risk_warning = self.tr('Risk Warning')
        self.error_title = self.tr('Error')
        self.notification_title = self.tr('Notification')

        self.get_ROOT_permissions_tips = self.tr(
            'After obtaining ROOT access, this software will have full control and operation over your device. This '
            'could lead to irreversible damage to your device, and the author will not be held responsible for any '
            'consequences arising from this. If you believe you are familiar with ROOT-related operations, '
            'you may proceed.')

        self.error_get_superuser_failed = self.tr(
            'Failed to obtain superuser permissions, please check if the device is rooted and allows Shell ('
            'com.android.shell) to access superuser requests.')
        self.error_device_adb_not_found = self.tr(
            'Device not found. Please check if the data cable is connected correctly or if the IP address input is '
            'accurate. This could also be due to issues with the ADB program.')
        self.error_no_device = self.tr('No device available for operation. Please connect to a device first.')

        self.stop_operation_success = self.tr('Operation canceled or permission acquisition failed.')
        self.getting_root_title = 'ROOT'
        self.getting_root_content = self.tr(
            'Attempting to acquire superuser permissions. Please allow the request on your device.')
        self.getting_root_success = self.tr('Superuser permissions obtained successfully. Please use with caution.')

        self.safety_app_package_name = self.tr('Package Name')
        self.safety_app_name = self.tr('APK Name')
        self.safety_app_apk_path = self.tr('APK Path')
        self.safety_app_type = self.tr('APP TYPE')
        self.safety_uninstall_app_warn = self.tr('Are you sure you want to uninstall this app?')
        self.safety_uninstall_system_app_warn = self.tr(
            'This seems to be a system app. Uninstalling it could potentially cause system damage. Do you still want '
            'to uninstall it?')
        self.safety_disable_app_warn = self.tr('Are you sure you want to disable this app?')
        self.safety_disable_system_app_warn = self.tr(
            'This seems to be a system app. Disabling it could potentially cause system damage. Do you still want to '
            'disable it?')
        self.safety_enable_app_warn = self.tr('Are you sure you want to enable this app?')
        self.safety_uninstall_success = self.tr('Uninstall Successful')
        self.safety_disable_success = self.tr('Disable Successful')
        self.safety_enable_success = self.tr('Enable Successful')
        self.safety_set_app_enable_error = self.tr('Unable to modify app enable state. This might require you to enable ROOT mode.')
        self.NO_DATA = self.tr('NO DATA')

        self.choose_dir = self.tr('Choose a directory')
