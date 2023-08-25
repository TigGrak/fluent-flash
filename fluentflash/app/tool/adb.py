#!/usr/bin/env python
# -*- coding:utf-8 -*-
# adb tools


import subprocess
import time
import re
import signal
from ..common.config import cfg
from ..common.runtime import rt
from ..common.translator import Translator
from ..common.signal_bus import signalKey, signalBus
from functools import wraps


class Command:
    def __init__(self):
        # device id
        """
        Usually, the device ID is empty at the beginning.
        After obtaining the list of devices, set the device ID at first.
        """
        # adb basic command
        self.cmd_adb_info = ['version']
        self.cmd_adb_devices = ['devices']
        self.cmd_adb_kill_server = ['kill-server']
        self.cmd_adb_start_server = ['start-server']

        # root
        self.cmd_adb_su = 'su -c'

        self.device = rt.DEVICE_ID
        self.host = ''

        self.__initDeviceCMD()
        self.__initConnectCMD()

    def __initDeviceCMD(self):
        # adb shell command (with device id)
        self.cmd_device_model = ['-s', self.device, 'shell', 'getprop', 'ro.product.model']
        self.cmd_device_memory = ['-s', self.device, 'shell',
                                  "expr $(cat /proc/meminfo | grep MemTotal | awk '{print $2}') / 1024 / 1024"]
        self.cmd_device_storage = ['-s', self.device, 'shell', 'df -h /sdcard']
        self.cmd_device_manufacture = ['-s', self.device, 'shell', 'getprop', 'ro.product.manufacturer']
        self.cmd_device_android_version = ['-s', self.device, 'shell', 'getprop', 'ro.build.version.release']
        self.cmd_device_fingerprint = ['-s', self.device, 'shell', 'getprop', 'ro.build.fingerprint']
        self.cmd_device_kernel_version = ['-s', self.device, 'shell', 'uname', '-r']
        self.cmd_device_baseband_version = ['-s', self.device, 'shell', 'getprop', 'gsm.version.baseband']
        self.cmd_device_security_patch_date = ['-s', self.device, 'shell', 'getprop', 'ro.build.version.security_patch']
        self.cmd_device_get_superuser = ['-s', self.device, 'shell', self.cmd_adb_su, 'echo', '"Success"']
        self.cmd_device_get_global_device_name = ['-s', self.device, 'shell', 'settings', 'get', 'global',
                                                  'device_name']
        self.cmd_device_get_package_list = ['-s', self.device, 'shell', 'pm', 'list', 'packages', '-f']
        self.cmd_device_get_system_app = ['-s', self.device, 'shell', 'pm', 'list', 'packages', '-s']
        self.cmd_device_get_disable_app = ['-s', self.device, 'shell', 'pm', 'list', 'packages', '-d']

        self.cmd_device_push = ['-s', self.device, 'push']
        self.cmd_device_pull = ['-s', self.device, 'pull']
        self.cmd_device_uninstall_app = ['-s', self.device, 'shell', 'pm', 'uninstall', '--user 0']
        self.cmd_device_enable_app = ['-s', self.device, 'shell', 'pm', 'enable']
        self.cmd_device_disable_app = ['-s', self.device, 'shell', 'pm', 'disable']
        self.cmd_device_chmod = ['-s', self.device, 'shell', 'chmod', '770']

        self.cmd_device_aapt = ['-s', self.device, 'shell', f'{cfg.cachePath}/aapt', 'dump', 'badging']

        # adb push ./aapt /data/local/tmp/fluent_flash/aapt
        # adb shell chmod 770 /data/local/tmp/fluent_flash/aapt

    def __initConnectCMD(self):
        # adb connect command
        self.cmd_connect = ['connect', self.host]

    def setDeviceID(self, device):
        """Set device id after get device list"""
        self.device = device
        self.__initDeviceCMD()

    def setHost(self, host):
        """Set host after get host list"""
        self.host = host
        self.__initConnectCMD()

    def creatCMDCheckGroup(self):
        """Create every command when run"""


class ADBTool:
    def __init__(self, adb_path, log_path="./adbLog.log", if_log=True):
        self.t = Translator()
        self.command = Command()
        self.adb_path = adb_path
        self.log_path = log_path
        self.if_log = if_log

        self.checkCMDError = {}

    def adbLog(func):
        """Get adb log and save to file."""

        @wraps(func)
        def inner(self, *args, **kwargs):
            if not self.if_log:
                return func(self, *args, **kwargs)
            with open(self.log_path, 'a+', encoding="UTF-8") as f:
                cmd = ''.join(f"{i} " for i in args[0])

                stdout, error = func(self, *args, **kwargs)
                stdout = stdout.strip()
                error = error.strip()
                f.write(f"###{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}###\n")
                f.write(f"cmd>>>{cmd}\n")
                if stdout:
                    f.write(f"stdout>>>{stdout}\n")
                if error:
                    f.write(f"error>>>{error}\n")
                f.write("################\n\n")
            return stdout, error

        return inner

    @adbLog
    def run(self, command, input_=''):
        """Run a single-line command with the option to preset an input in advance."""
        # run
        process = subprocess.Popen(command,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   encoding='utf-8',
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

        rt.setRunCmdProcess(process)

        try:
            if not rt.run_cmd_process_status:
                raise Exception(f'error: {self.t.stop_operation_success}')
            # input input_ and return
            return process.communicate(input_)

        except Exception as e:
            return '', str(e)
        finally:
            process.terminate()
            process.wait()


class ADBUse:
    def __init__(self):
        self.command = Command()
        self.if_log = cfg.ifLog.value
        self.adb_tool = ADBTool(cfg.ADBPath.value, if_log=self.if_log)
        self.adb_path = cfg.ADBPath.value

    # command completion
    def commandCompletion(self, cmd):
        """Command completion"""

        command = list(cmd)
        # check if need root
        if rt.ROOT and len(command) > 3 and command[2] == 'shell':
            command.insert(3, self.command.cmd_adb_su)

        # insert adb path
        command.insert(0, self.adb_path)
        return command

    def checkError(self, stdout, error, cus_check=None):
        """Check if there is an error in the command."""

        if cus_check is None:
            cus_check = ['adb: error:.*', '\[WinError 2\].*', 'adb\.exe: device .* not found', 'error:.*',
                         'Failure \[.*\]']

        for i in cus_check:
            if re.search(i, stdout):
                return stdout.strip()
            if re.search(i, error):
                return error.strip()
        return None

    def tryFunc(func):
        """Try to run the function and return the result."""

        @wraps(func)
        def inner(self, *args, **kwargs):
            try:
                rt.setRunCmdProcessStatus(True)
                return func(self, *args, **kwargs)
            except Exception as e:
                return {'status': signalKey.ERROR, 'info': {}, 'error': str(e)}
            finally:
                rt.setRunCmdProcess(None)

        return inner

    def run(self, command, input_=''):
        """Run a single-line command with the option to preset an input in advance."""

        run_cmd = self.commandCompletion(command)
        # print(run_cmd)
        stdout, error = self.adb_tool.run(run_cmd, input_)
        if (error := self.checkError(stdout, error)) is not None:
            error_cmd = ''.join(f"{i} " for i in run_cmd)
            raise Exception(f"cmd>>>{error_cmd}\nout>>>{error}\n")
        return stdout, error

    @tryFunc
    def checkDevice(self, host=None):
        """Check if the device is connected and return the device ID and name."""

        # restart adb server
        # self.run(['kill-server'])
        # self.run(['start-server'])

        if host is not None:
            self.command.setHost(host)
            self.run(self.command.cmd_connect)

        devices_list_raw, error = self.run(self.command.cmd_adb_devices)

        devices_list_raw = devices_list_raw.strip()
        devices_list_raw = devices_list_raw.split('\n')
        # remove first line
        devices_list_raw.pop(0)

        devices_list = [
            device.split('\t')[0]
            for device in devices_list_raw
            if device and device.split('\t')[1] == 'device'
        ]
        devices_info = {'info': {}}
        for device in devices_list:
            devices_info['info'][device] = \
                self.run(['-s', device, 'shell', 'settings', 'get', 'global', 'device_name'])[0].strip()

        if len(devices_info['info']) == 0:
            devices_info['status'] = signalKey.NOT_FOUND
        else:
            devices_info['status'] = signalKey.FOUND

        return devices_info

    @tryFunc
    def getDeviceInfo(self):
        """Get device information and return a dictionary."""

        self.command.setDeviceID(rt.DEVICE_ID)
        # if device_id is ip format
        device_connect_type = 'TCP' if rt.DEVICE_ID.find(':') != -1 else 'USB'
        # get device name
        device_name, _ = self.run(self.command.cmd_device_get_global_device_name)
        device_name = device_name.strip()
        # get device model
        device_model, _ = self.run(self.command.cmd_device_model)
        device_model = device_model.strip()
        # get storage
        device_storage_detailed, _ = self.run(self.command.cmd_device_storage)
        device_storage_detailed = device_storage_detailed.strip().split('\n')
        device_storage = None
        for line in device_storage_detailed:
            if "/storage/emulated" in line:
                parts = line.split()
                if len(parts) >= 2:
                    device_storage = parts[1]
                    break
        # get memory
        device_memory, _ = self.run(self.command.cmd_device_memory)
        device_memory = f"{device_memory.strip()}G"
        # get device manufacture
        device_manufacture, _ = self.run(self.command.cmd_device_manufacture)
        device_manufacture = device_manufacture.strip()
        # get device android version
        device_android_version, _ = self.run(self.command.cmd_device_android_version)
        device_android_version = device_android_version.strip()
        # get ui version,ui build
        device_ui, _ = self.run(self.command.cmd_device_fingerprint)
        device_ui = device_ui.strip().split('/')

        if len(device_ui) >= 4:
            ui_build = device_ui[3]
            ui_version = device_ui[4]
        else:
            ui_build = ''
            ui_version = ''

        # get device kernel version
        device_kernel_version, _ = self.run(self.command.cmd_device_kernel_version)
        device_kernel_version = device_kernel_version.strip()
        # get baseband version
        device_baseband_version, _ = self.run(self.command.cmd_device_baseband_version)
        device_baseband_version = device_baseband_version.strip().split(',')[0]
        # get security patch date
        device_security_patch_date, _ = self.run(self.command.cmd_device_security_patch_date)
        device_security_patch_date = device_security_patch_date.strip()
        # get adb info
        adb_info, _ = self.run(self.command.cmd_adb_info)
        adb_info = adb_info.strip().split('\n')
        if len(adb_info) >= 4:
            # default adb
            # Android Debug Bridge version 1.0.41
            adb_version = f"ADB {adb_info[0].split(' ')[4]}"
            # Windows version
            windows_version = f"Windows {adb_info[3].split(' ')[3]}"
        else:
            adb_version = ''
            windows_version = ''

        info = {'device_id': rt.DEVICE_ID,
                'device_connect_type': device_connect_type,
                'device_name': device_name,
                'device_model': device_model,
                'device_manufacture': device_manufacture,
                'device_android_version': device_android_version,
                'ui_build': ui_build,
                'ui_version': ui_version,
                'device_kernel_version': device_kernel_version,
                'device_baseband_version': device_baseband_version,
                'device_security_patch_date': device_security_patch_date,
                'adb_version': adb_version,
                'windows_version': windows_version,
                'device_storage': device_storage,
                'device_memory': device_memory}

        return {'status': signalKey.SUCCESS, 'info': info, 'error': ''}

    @tryFunc
    def checkSU(self):
        """Check if the device has root permission."""

        stdout, _ = self.run(self.command.cmd_device_get_superuser)
        stdout = stdout.strip()
        return {'status': signalKey.SUCCESS, 'info': stdout.find('Success') != -1, 'error': ''}

    @tryFunc
    def push(self, local_path, remote_path):
        """Push a file to the device."""

        stdout, error = self.run(self.command.cmd_device_push + [local_path, remote_path])
        _, _ = self.run(self.command.cmd_device_chmod + [remote_path])
        return {
            'status': signalKey.SUCCESS,
            'info': {'stdout': stdout, 'error': error},
            'error': ''
        }

    def pull(self, rp, lp):
        """Pull a file from the device."""

        self.run(self.command.cmd_device_pull + [rp, lp])
        return {
            'status': signalKey.SUCCESS,
            'info': '',
            'error': ''
        }

    @tryFunc
    def extractAPKFile(self, file_list):
        """Extract apk file from device."""
        task_count = len(file_list)
        per_progress = 100 / task_count
        signalBus.extract_apk.emit(
            {'status': signalKey.SUCCESS, 'info': {'type': signalKey.SET_PROGRESS, 'progress': 0}, 'error': ''})
        for file in file_list:
            rp = file[1]
            lp = file[0]
            self.pull(rp, lp)
            per_progress += 100 / task_count
            signalBus.extract_apk.emit(
                {'status': signalKey.SET_PROGRESS, 'info': {'type': signalKey.SET_PROGRESS, 'progress': per_progress},
                 'error': ''})
        return {
            'status': signalKey.SUCCESS,
            'info': {'type': signalKey.SUCCESS, 'info': ''},
            'error': ''
        }

    @tryFunc
    def uninstallAPP(self, package_name):
        package = [package_name]
        stdout, error = self.run(self.command.cmd_device_uninstall_app + package)
        return {
            'status': signalKey.SUCCESS,
            'info': stdout,
            'error': error
        }

    @tryFunc
    def setAPPEnable(self, package_name, enable):
        package = [package_name]
        stdout, error = (
            self.run(self.command.cmd_device_enable_app + package)) \
            if enable else (
            self.run(self.command.cmd_device_disable_app + package))
        return {
            'status': signalKey.SUCCESS,
            'info': {'stdout': stdout, 'type':enable},
            'error': error
        }

    @tryFunc
    def getApps(self):
        """Get all apps on the device and return a dictionary."""

        package_list_raw, error = self.run(self.command.cmd_device_get_package_list)
        package_list_raw = package_list_raw.strip().split('\n')
        per_progress = 100 / len(package_list_raw)
        signalBus.refresh_device_app_list.emit({'status': signalKey.SET_PROGRESS, 'info': per_progress, 'error': ''})

        disable_app_list_raw, error = self.run(self.command.cmd_device_get_disable_app)
        disable_app_list_raw = disable_app_list_raw.strip().split('\n')
        disable_app_list = [i.split(':')[-1] for i in disable_app_list_raw]

        system_app_list_raw, error = self.run(self.command.cmd_device_get_system_app)
        system_app_list_raw = system_app_list_raw.strip().split('\n')
        system_app_list = [i.split(':')[-1] for i in system_app_list_raw]

        print(disable_app_list)
        print(system_app_list)

        # {'com.xx.xx':{'path':'/data/app/com.xx.xx.apk','name':{},'version':'','sdkVersion':'','native-code':''}}
        info = {}
        for package in package_list_raw:
            # package_name:last one com.xx.xx
            package_name = package.split('=')[-1]
            # package_path: remove package: and =package_name
            package_path = package.replace('package:', '')
            package_path = f"{package_path.replace(f'.apk={package_name}', '')}.apk"
            info[package_name] = {}

            app, error = self.run(self.command.cmd_device_aapt + [package_path])
            app = app.strip() or ''

            app_name = {}
            sdkVersion = ''
            version = ''
            native_code = ''

            for line in app.splitlines():
                # get version
                if line.startswith('package:'):
                    line = line.split(' ')
                    for ver in line:
                        if ver.startswith('versionName'):
                            version = ver.split('=')[1].replace("'", '')

                # get android sdk version
                elif line.startswith('sdkVersion:'):
                    line = line.split(':')
                    sdkVersion = line[1].replace("'", '')

                # get app name
                elif line.startswith('application-label'):
                    line = line.split(':')
                    # if line[0] include application-label-，remove application-label-
                    if line[0].startswith('application-label-'):
                        line[0] = line[0].replace('application-label-', '')
                    # if line[0] is application-label,change it to all
                    if line[0] == 'application-label':
                        line[0] = 'all'

                    line[1] = line[1].replace("'", '')
                    app_name[line[0]] = line[1]

                # get native code
                elif line.startswith('native-code:'):
                    line = line.split(':')
                    native_code = line[1].replace("'", '')
                    native_code = native_code.strip()

            info[package_name]['enable'] = package_name not in disable_app_list
            info[package_name]['type'] = 'SYSTEM APP' if package_name in system_app_list else 'USER APP'
            info[package_name]['path'] = package_path
            info[package_name]['name'] = app_name
            info[package_name]['version'] = version
            info[package_name]['sdkVersion'] = sdkVersion
            info[package_name]['native_code'] = native_code

            per_progress += 100 / len(package_list_raw)

            signalBus.refresh_device_app_list.emit(
                {'status': signalKey.SET_PROGRESS, 'info': per_progress, 'error': ''})
            signalBus.refresh_device_app_list.emit({'status': signalKey.SUCCESS, 'info': {
                package_name: {'path': package_path, 'name': app_name, 'version': version, 'sdkVersion': sdkVersion,
                               'native_code': native_code}}})

        return {'error': '', 'status': signalKey.SUCCESS, 'info': info}


# global adb
adb = ADBUse()
