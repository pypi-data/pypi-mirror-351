#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： Wentao Zheng
# datetime： 2024/3/4 21:13 
# ide： PyCharm
import os
import sys
import shlex
import platform
import subprocess
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

# 自定义库
from dynamic_scenes.observation import Observation
import VehicleModel_dll.VehicleModel as vml

class KineticsModelStarter():
    def __init__(self, observation: Observation):
        self.step_time = observation.test_setting['dt']
        self.x, self.y, self.yaw, self.v = self._get_init_state_of_ego(observation)
        abs_dll_path = os.path.abspath(os.path.join((os.path.dirname(__file__)),'../VehicleModel_dll', "VehicleModelPython.dll"))
        abs_so_path = os.path.abspath(os.path.join((os.path.dirname(__file__)),'../VehicleModel_dll', "libcombined.so"))
        # print("dll路径:", abs_dll_path)
        if self._judge_platform() == 'win':
            self.model_dll = vml.load_VehicleModel_dll(abs_dll_path)
        elif self._judge_platform() == 'linux':
            self.model_dll = vml.load_VehicleModel_so(abs_so_path)
        if self.model_dll == None:
            print("加载库文件失败")
            sys.exit(1)
        self.car = vml.CreateVehicleModel(self.model_dll)
    
    def kinetic_step(self, action, state):
        # print(f"action:{action}")
        new_state, _ = vml.VehicleModel_step(self.model_dll, self.car, action, state, self.step_time)
        return new_state
    
    def kinetic_terminate(self):
        vml.DeleteVehicleModel(self.model_dll, self.car)

    def _get_init_state_of_ego(self, observation:Observation):
        x = observation.vehicle_info['ego']['x']
        y = observation.vehicle_info['ego']['y']
        yaw = observation.vehicle_info['ego']['yaw_rad']
        v0 = observation.vehicle_info['ego']['v_mps']
        return x,y,yaw,v0

    def _judge_platform(self):
        os_type = platform.system()
        if os_type == "Windows":
            return 'win'
        elif os_type == "Linux" or os_type == "Darwin":
            return 'linux'
        else:
            print(f"不支持的操作系统: {os_type}")