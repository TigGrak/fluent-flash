#!/usr/bin/env python
# -*- coding:utf-8 -*-
# adb tools


import subprocess
from ..common.config import cfg
from ..common.runtime import rt
from ..common.signal_bus import signalKey


class Command:
    def __init__(self,device=""):
        #device id
        """
        Usually, the device ID is empty at the beginning.
        After obtaining the list of devices, set the device ID at first.
        """
        self.device = device

        #adb basic command
        self.cmd_adb_info = ['version']
        self.cmd_adb_devices = ['devices']
        self.cmd_adb_kill_server = ['kill-server']
        self.cmd_adb_start_server = ['start-server']

        #root
        self.cmd_adb_su = 'su -c'

        #adb shell command (with device id)
        self.cmd_device_model = ['-s',self.device,'shell','getprop','ro.product.model']
        self.cmd_device_memory = ['-s',self.device,'shell',"expr $(cat /proc/meminfo | grep MemTotal | awk '{print $2}') / 1024 / 1024"]
        self.cmd_device_storage = ['-s',self.device,'shell','df -h /sdcard']
        self.cmd_device_manufacture = ['-s',self.device,'shell','getprop','ro.product.manufacturer']
        self.cmd_device_android_version = ['-s',self.device,'shell','getprop','ro.build.version.release']
        self.cmd_device_fingerprint = ['-s',self.device,'shell','getprop','ro.build.fingerprint']
        self.cmd_device_kernel_version = ['-s',self.device,'shell','uname','-r']
        self.cmd_device_baseband_version = ['-s',self.device,'shell','getprop','gsm.version.baseband']
        self.cmd_device_security_patch_date = ['-s',self.device,'shell','getprop','ro.build.version.security_patch']
        self.cmd_device_get_superuser = ['-s', self.device, 'shell', self.cmd_adb_su,'echo','"Success"']
        self.cmd_device_get_global_device_name = ['-s',self.device,'shell','settings','get','global','device_name']

        self.cmd_device_get_package_list = ['-s',self.device,'shell','pm','list','packages','-f']



    def setDeviceID(self,device):
        """Set device id after get device list"""
        self.device = device







class ADBTool:
    def __init__(self,adb_path):
        self.command = Command()
        self.adb_path = adb_path
        self.device_id = None

    def run(self,command,input_=''):
        """Run a single-line command with the option to preset an input in advance."""

        run_cmd = list(command)

        # check if need root
        if rt.ROOT:
            run_cmd.insert(0,self.command.cmd_adb_su)

        # insert adb path
        run_cmd.insert(0,self.adb_path)

        print(run_cmd)

        #run
        process = subprocess.Popen(run_cmd,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               encoding='utf-8')

        #input input_ and return
        return process.communicate(input_)

    def checkDevice(self,host=None):
        """Check if the device is connected and return the device ID and name."""

        # restart adb server
        #self.run(['kill-server'])
        #self.run(['start-server'])

        if host is not None:
            self.run(['connect',host])

        devices_list_raw,_ = self.run(['devices'])
        devices_list_raw = devices_list_raw.strip()
        devices_list_raw = devices_list_raw.split('\n')
        #remove first line
        devices_list_raw.pop(0)

        devices_list = []
        for device in devices_list_raw:
            if device and device.split('\t')[1] == 'device':
                devices_list.append(device.split('\t')[0])

        devices_info = {'devices': {}}
        for device in devices_list:
            devices_info['devices'][device] = self.run(['-s',device,'shell','settings','get','global','device_name'])[0].strip()

        if len(devices_info['devices']) == 0:
            devices_info['status'] = signalKey.NOT_FOUND
        else:
            devices_info['status'] = signalKey.FOUND

        return devices_info



    def getDeviceInfo(self,device_id):
        """Get device information and return a dictionary."""

        self.device_id = device_id
        self.command.setDeviceID(device_id)
        # if device_id is ip format
        if device_id.find(':') != -1:
            device_connect_type = 'TCP'
        else:
            device_connect_type = 'USB'
        # get device brand
        device_name,_ = self.run(self.command.cmd_device_get_global_device_name)
        device_name = device_name.strip()
        # get device model
        device_model,_ = self.run(self.command.cmd_device_model)
        device_model = device_model.strip()
        #get storage
        device_storage_detailed,_ = self.run(self.command.cmd_device_storage)
        device_storage_detailed = device_storage_detailed.strip().split('\n')
        device_storage = None
        for line in device_storage_detailed:
            if "/storage/emulated" in line:
                parts = line.split()
                if len(parts) >= 2:
                    device_storage = parts[1]
                    break
        #get memory
        device_memory,_ = self.run(self.command.cmd_device_memory)
        device_memory = f"{device_memory.strip()}G"
        #get device manufacture
        device_manufacture,_ = self.run(self.command.cmd_device_manufacture)
        device_manufacture = device_manufacture.strip()
        # get device android version
        device_android_version,_ = self.run(self.command.cmd_device_android_version)
        device_android_version = device_android_version.strip()
        #get ui version,ui build
        device_ui,_ = self.run(self.command.cmd_device_fingerprint)
        device_ui = device_ui.strip().split('/')
        ui_build = device_ui[3]
        ui_version = device_ui[4]
        # get device kernel version
        device_kernel_version,_ = self.run(self.command.cmd_device_kernel_version)
        device_kernel_version = device_kernel_version.strip()
        #get baseband version
        device_baseband_version,_ = self.run(self.command.cmd_device_baseband_version)
        device_baseband_version = device_baseband_version.strip().split(',')[0]
        # get security patch date
        device_security_patch_date,_ = self.run(self.command.cmd_device_security_patch_date)
        device_security_patch_date = device_security_patch_date.strip()
        # get adb info
        adb_info,_ = self.run(self.command.cmd_adb_info)
        adb_info = adb_info.strip().split('\n')
        # default adb
        #Android Debug Bridge version 1.0.41
        adb_version = f"ADB {adb_info[0].split(' ')[4]}"
        #Windows version
        windows_version = f"Windows {adb_info[3].split(' ')[3]}"
        return {'device_id':device_id,
                'device_connect_type':device_connect_type,
                'device_name':device_name,
                'device_model':device_model,
                'device_manufacture':device_manufacture,
                'device_android_version':device_android_version,
                'ui_build':ui_build,
                'ui_version':ui_version,
                'device_kernel_version':device_kernel_version,
                'device_baseband_version':device_baseband_version,
                'device_security_patch_date':device_security_patch_date,
                'adb_version':adb_version,
                'windows_version':windows_version,
                'device_storage':device_storage,
                'device_memory':device_memory}

    def checkSU(self):
        """Check if the device has root permission."""

        stdout,_ = self.run(self.command.cmd_device_get_superuser)
        stdout =  stdout.strip()
        if stdout.find('Success') != -1:
            return True
        else:
            return False

    def getApps(self):
        app_info = {'status':'','info':{},'error':''}
        package_list_raw,error = self.run(self.command.cmd_device_get_package_list)
        package_list_raw = package_list_raw.strip().split('\n')
        error = error.strip()
        if error:
            app_info['status'] = signalKey.ERROR
            app_info['error'] = error
            return app_info

        info = {}
        #package:/aa==/bb==/cc==/xyz.apk=com.xx.xx
        for i in package_list_raw:
            # package_name:last one com.xx.xx
            package_name = i.split('=')[-1]
            # package_path: remove package: and =package_name
            package_path = i.replace('package:','')
            package_path = f"{package_path.replace(f'.apk={package_name}','')}.apk"
            info[package_name] = package_path
        app_info['status'] = signalKey.SUCCESS
        app_info['info'] = info
        return app_info



# global adb
adb = ADBTool(cfg.ADBPATH)