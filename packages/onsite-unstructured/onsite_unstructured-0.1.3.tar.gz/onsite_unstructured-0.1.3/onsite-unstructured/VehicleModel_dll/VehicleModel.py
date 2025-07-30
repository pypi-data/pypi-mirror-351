# 本文件将dll文件中的函数调用流程封装为四个基本文件
# 1. load_VehicleModel_dll(dll_path)  # 载入dll文件并核验
# 2. CreateVehicleModel  # 创建并返回一个车辆模型指针，用于管理一台车的所有状态转移，与其他车分隔开
# 3. VehicleModel_step  # 对一台车进行step_time时间长度下的步进状态转移
# 4. DeleteVehicleModel  # 删除车辆模型指针
from ctypes import *
import os
import sys
import math
import time

class ExtU_VehicleModelPython_T(Structure):
    _fields_ = [
        ("acc", c_double),
        ("gear", c_double),
        ("steer", c_double),
        ("slope", c_double),
        ("x0", c_double),
        ("y0", c_double),
        ("yaw", c_double),
        ("v0", c_double),
    ]

# 输出结构体
class ExtY_VehicleModelPython_T(Structure):
    _fields_ = [
        ("x", c_double),
        ("y", c_double),
        ("phi", c_double),
        ("velocity", c_double),
    ]


# ******载入so文件并核验****** #
def load_VehicleModel_so(so_path):
    try:
        model_so = CDLL(so_path)  # 或 cdll.LoadLibrary(dll_path)
        print("so文件加载成功")
    except OSError as e:
        print(f"so文件加载失败: {e}")
        model_so = None
        return model_so
    required_functions = ["CreateVehicleModel", "Step", "DeleteVehicleModel",
                        "SetInputs", "GetOutputs", "Initialize", "Terminate"]
    for func in required_functions:
        if not hasattr(model_so, func):
            print(f"错误：so文件未导出函数 {func}")
            model_so = None
            return model_so
        # else:
            # print(f"{func}函数 已成功导出")
    # ******声明函数参数类型和返回类型****** #
    model_so.CreateVehicleModel.argtypes = []
    model_so.CreateVehicleModel.restype = c_void_p  # 返回类指针

    model_so.DeleteVehicleModel.argtypes = [c_void_p]  # 参数为指针
    model_so.DeleteVehicleModel.restype = None

    model_so.SetInputs.argtypes = [c_void_p, POINTER(ExtU_VehicleModelPython_T)]
    model_so.SetInputs.restype = None

    model_so.GetOutputs.argtypes = [c_void_p]
    model_so.GetOutputs.restype = POINTER(ExtY_VehicleModelPython_T)

    model_so.Initialize.argtypes = [c_void_p]
    model_so.Initialize.restype = None

    model_so.Step.argtypes = [c_void_p]
    model_so.Step.restype = None

    model_so.Terminate.argtypes = []
    model_so.Terminate.restype = None
    # ******成功声明函数参数类型和返回类型****** #
    return model_so

# ******载入DLL文件并核验****** #
def load_VehicleModel_dll(dll_path):
    try:
        model_dll = CDLL(dll_path)  # 或 cdll.LoadLibrary(dll_path)
        print("DLL 加载成功")
    except OSError as e:
        print(f"DLL 加载失败: {e}")
        model_dll = None
        return model_dll

    required_functions = ["CreateVehicleModel", "Step", "DeleteVehicleModel",
                        "SetInputs", "GetOutputs", "Initialize", "Terminate"]
    for func in required_functions:
        if not hasattr(model_dll, func):
            print(f"错误：DLL 未导出函数 {func}")
            model_dll = None
            return model_dll
        # else:
            # print(f"{func}函数 已成功导出")
    # ******声明函数参数类型和返回类型****** #
    model_dll.CreateVehicleModel.argtypes = []
    model_dll.CreateVehicleModel.restype = c_void_p  # 返回类指针

    model_dll.DeleteVehicleModel.argtypes = [c_void_p]  # 参数为指针
    model_dll.DeleteVehicleModel.restype = None

    model_dll.SetInputs.argtypes = [c_void_p, POINTER(ExtU_VehicleModelPython_T)]
    model_dll.SetInputs.restype = None

    model_dll.GetOutputs.argtypes = [c_void_p]
    model_dll.GetOutputs.restype = POINTER(ExtY_VehicleModelPython_T)

    model_dll.Initialize.argtypes = [c_void_p]
    model_dll.Initialize.restype = None

    model_dll.Step.argtypes = [c_void_p]
    model_dll.Step.restype = None

    model_dll.Terminate.argtypes = []
    model_dll.Terminate.restype = None
    # ******成功声明函数参数类型和返回类型****** #
    return model_dll
    
# ******成功载入DLL文件****** #


def CreateVehicleModel(model_dll):
    model_ptr = model_dll.CreateVehicleModel()
    if not model_ptr:
        model_ptr = None
        print("错误：创建模型实例失败")
    else:
        model_dll.Initialize(model_ptr)
        # print(f"模型实例创建成功")
    return model_ptr


# 4. 设置输入参数（yaw和steer都是弧度制）,slope为正表示下坡
# 速度为0时，在最初的0.005s内会有些奇怪的抖动（也就是50次step），matlab中运行模型也会这样，但后续会恢复正常，所以只要执行1000步获取0.1s后的状态就可以忽略这一奇异点表现
# 速度不为0就不会有这种抖动，哪怕只执行1次step也表现的很正常，总而言之只要目标是获取0.1s后的状态怎样都正常
# 比对matlab和python的输出，发现python的输出与matlab直接运行simulink模型的输出有一定偏差，
# 但偏差量较小，速度上无论什么速度基本都只有0.001m/s的偏差，位置偏差和转向时的航向偏差则比1e-3更小，所以可以忽略不计
# acc为正代表踩油门，负代表踩刹车，gear=1为前进，gear=3为倒车，gear=2为驻车，向前开v为正，向后开v为负
# 向后开也是gear=3，acc为正，v为负
# action = (acc, gear, steer, slope), state = (x, y, yaw, v),分别是两个元组
def VehicleModel_step(model_dll, model_ptr, action, state, step_time=0.1):
    input_data = ExtU_VehicleModelPython_T(
        acc=action[0],      # 根据实际需求赋值
        gear=action[1],
        steer=action[2],
        slope=action[3],
        x0=state[0],
        y0=state[1],
        yaw=state[2],
        v0=state[3]
    )
    model_dll.SetInputs(model_ptr, byref(input_data))

    start_time = time.time()
    model_dll.Step(model_ptr)

    # 5. 执行step计算0.1s后的状态
    # 模型的基础采样步长是0.0001s，所以想要获得0.1s后的状态就需要执行1000步
    num_step = int(step_time*1e4)
    # print(num_step)
    for i in range(num_step):
        output_ptr = model_dll.GetOutputs(model_ptr)
        output_data = output_ptr.contents  # 解引用指针
        input_data = ExtU_VehicleModelPython_T(
        acc=action[0],      # 根据实际需求赋值
        gear=action[1],
        steer=action[2],
        slope=action[3],
        x0=output_data.x,
        y0=output_data.y,
        yaw=output_data.phi,
        v0=output_data.velocity
        )
        model_dll.SetInputs(model_ptr, byref(input_data))
        model_dll.Step(model_ptr)
    end_time = time.time()

    # 6. 获取输出结果
    output_ptr = model_dll.GetOutputs(model_ptr)
    output_data = output_ptr.contents  # 解引用指针
    new_state = (output_data.x, output_data.y, output_data.phi, output_data.velocity)
    cost_time_ms = 1000*(end_time-start_time)
    # print("输出结果:")
    # print(f"x = {output_data.x}")
    # print(f"y = {output_data.y}")
    # print(f"phi = {output_data.phi}")
    # print(f"velocity = {output_data.velocity}")
    # print(f"step函数耗时：{cost_time_ms}ms")
    return new_state, cost_time_ms

def DeleteVehicleModel(model_dll, model_ptr):
    model_dll.DeleteVehicleModel(model_ptr)
    model_dll.Terminate()