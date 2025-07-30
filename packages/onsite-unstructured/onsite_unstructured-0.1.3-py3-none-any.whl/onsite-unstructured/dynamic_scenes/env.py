# 内置库 
import os
import sys
import shlex
import subprocess
import numpy as np
from PIL import Image
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import importlib
import json
# 第三方库
from typing import Dict,List,Tuple,Optional,Union

# 自定义库
from dynamic_scenes.observation import Observation
from dynamic_scenes.controller import Controller
from dynamic_scenes.recorder import Recorder
from dynamic_scenes.visualizer import Visualizer
from dynamic_scenes.lookup import CollisionLookup
from dynamic_scenes.kinetics_model import KineticsModelStarter

class Env():
    """仿真环境读取及迭代过程,simulation"""
    def __init__(self):
        self.controller = Controller()
        self.recorder = Recorder()
        self.visualizer = Visualizer()
        self.scene_type = "intersection"
    def get_slope(self, observation, height):
        z1 = height[20][20]
        dx = observation['vehicle_info']['ego']['shape']['length']*np.cos(observation['vehicle_info']['ego']['yaw_rad'])
        dy = observation['vehicle_info']['ego']['shape']['length']*np.sin(observation['vehicle_info']['ego']['yaw_rad'])
        x_idx = math.floor(dx+20)
        y_idx = math.floor(dy+20)
        x_idx = max(0, min(x_idx, 40))
        y_idx = max(0, min(y_idx, 40))
        z2 = height[x_idx][y_idx]

        distance = math.sqrt(dx ** 2 + dy ** 2)
        return -math.atan2((z2-z1), distance)

    def init_height_loader(self,scenario:dict, dir_inputs, scene_type='intersection') -> None:

        # 战区高程读取逻辑
        if scene_type == "B":
            self.location_temp = scenario['data']['scene_name'].split("_")[0]  # Bxxx
            height_file_path = os.path.abspath(os.path.join(dir_inputs, 'Maps', 'bitmap', self.location_temp+'_global_map.json'))
            try:
                with open(height_file_path, 'r', encoding='utf-8') as height_file:
                    mission_height_json = json.load(height_file)
                data = mission_height_json.get('data')
                # battle_height是二维数组，查询方式是self.battle_height[y_pix][x_pix],y_pix和x_pix分别是高方向和宽方向上的像素索引，一般是物理坐标/resolution
                self.battle_height_info = [[-1 if item == "-1" else item for item in row] for row in data]
                self.battle_height = mission_height_json['metadata']['dimensions']['height']
                self.battle_width = mission_height_json['metadata']['dimensions']['width']
                self.battle_reso = mission_height_json['metadata']['dimensions']['resolution']

            except:
                print(f"### fail to load height data from {height_file_path}!")
        else:
            self.location_temp = scenario['data']['scene_name'].split("_")[0]  # jiangtong/dapai/shovel
            dir_current_file = os.path.dirname(__file__)  
            dir_parent_1 = os.path.dirname(dir_current_file) 
            data_path = os.path.abspath(os.path.join(dir_parent_1, 'data'))
            height_file_path = os.path.abspath(os.path.join(data_path, self.location_temp + '_block.npy'))
            try:
                self.points = np.load(height_file_path)
                self.points_dict = {(row[0], row[1]): row[2] for row in self.points}
            except:
                print(f"### fail to load height data from {height_file_path}!")

            map_path = os.path.join(dir_inputs,'Maps')
            semanticmap_path = os.path.join(map_path,'semantic_map')
            for item in os.listdir(semanticmap_path):
                if self.location_temp in item:
                    file_path = os.path.join(semanticmap_path, item)
                    if os.path.isfile(file_path):
                        try:
                            # 打开并加载 JSON 文件
                            with open(file_path, 'r', encoding='utf-8') as file:
                                data = json.load(file)
                            print(f"成功加载文件：{file_path}")
                            # 在这里处理 data
                        except json.JSONDecodeError:
                            print(f"错误：文件 {file_path} 不是有效的 JSON 格式！")
                        except Exception as e:
                            print(f"加载文件 {file_path} 时出错：{e}")
                    self.para1  = -data["bitmap_mask_PNG"]["UTM_info"]["point_southwest"][0]
                    self.para2 = data["bitmap_mask_PNG"]["canvas_edge_meter"][1]
                    self.para3 = data["bitmap_mask_PNG"]["UTM_info"]["point_southwest"][1]
        



    def make(self,scenario:dict, read_only=False, dir_inputs='', save_img_path='',kinetics_mode='simple', scene_type = "intersection") -> Tuple:
        """第一次进入读取环境信息.

        Args:
            scenario (dict): 动态场景输入信息.
            collision_lookup (CollisionLookup): 用于 ego车与(栅格化mask)边界 进行碰撞检测的预置数据.
            read_only (bool, optional): _description_. Defaults to False.

        Returns:
            Observation: 当前时刻环境观察结果;
            traj:全局的背景车辆轨迹数据;
        """
        self.scene_type = scene_type
        # 载入高程信息
        self.init_height_loader(scenario, dir_inputs, self.scene_type)

        observation,observation_all,traj = self.controller.init(scenario,kinetics_mode, self.scene_type)
        if kinetics_mode == "complex":
            self.kineticModel = KineticsModelStarter(observation)
            print("using complex kinetics model")
        else:
            raise ValueError("暂不提供这种动力学模式，请选择complex！")

        self.recorder.init(observation_all,scenario['file_info']['dir_outputs'],read_only)
        if self.scene_type == "B":
            self.visualizer.battle_init(observation_all,
                            scenario['test_settings']['visualize'],
                            scenario['test_settings']['save_fig_whitout_show'],
                            img_save_path=save_img_path) # 此处通过查看配置参数,True,设置运行过程中可视化打开;
        else:
            self.visualizer.init(observation_all,
                            scenario['test_settings']['visualize'],
                            scenario['test_settings']['save_fig_whitout_show'],
                            img_save_path=save_img_path) # 此处通过查看配置参数,True,设置运行过程中可视化打开;
        
        height = self.get_height(observation.format())
        
        return observation.format(), height
    
    def get_height(self, observation):
        result = []
        if self.scene_type=="B":
            for i in range(-20,21):
                col = []
                for j in range(-20, 21):
                    x = observation['vehicle_info']['ego']['x'] + i - observation['test_setting']['x_min']
                    y = observation['vehicle_info']['ego']['y'] + j - observation['test_setting']['y_min']
                    x_pix = int(x/self.battle_reso)
                    y_pix = int(y/self.battle_reso)
                    x_pix = min((len(self.battle_height_info[0])-1), max(x_pix, 0))
                    y_pix = min((len(self.battle_height_info)-1), max(y_pix, 0)) 
                    z_data = self.battle_height_info[y_pix][x_pix]
                    col.append(z_data)
                result.append(col)
        else:
            for i in range(-20, 21):  # 遍历 -20 到 20
                col = []
                for j in range(-20, 21):  # 遍历 -20 到 20
                    unround_x = (observation['vehicle_info']['ego']['x'] + i) + self.para1
                    unround_y = self.para2 - (observation['vehicle_info']['ego']['y'] + j) + self.para3
                    position_transformed = (round(int(unround_x)+0.5, 1), round(int(unround_y)+0.5, 1))  # 构造查询键

                    # 查询字典，如果不存在则返回 -1
                    z_data = self.points_dict.get(position_transformed, -1)
                    col.append(z_data)  # 将高度值添加到当前列
                result.append(col)  # 将当前列添加到结果列表
        return result
        

    def step(self,action:Tuple[float,float,int],traj_future:Dict,observation_last:Observation,traj=200, path_planned=None, vis_cir_open=False) -> Observation:
        """迭代过程"""
        last_height = self.get_height(observation_last)
        last_slope = self.get_slope(observation_last,last_height)
        observation = self.controller.step(self,action,traj_future,observation_last,traj, path_planned, last_slope, last_height=None, vis_cir_open=vis_cir_open)  # 使用车辆运动学模型单步更新场景;
        height = self.get_height(observation.format())
        #self.recorder.record(observation)
        # self.visualizer.update(observation)  
        #self.visualizer.update(observation,traj_future,observation_last,traj)# 更新场景后,使用更新的ego车辆位置进行可视化;【CZF】添加预测轨迹+真实轨迹的比较
        
        return observation.format(), height
    
    def kinetic_step(self, action, state):
        return self.kineticModel.kinetic_step(action, state)
    
    def stop_car_model(self):
        if hasattr(self, 'kineticModel'):
            self.kineticModel.kinetic_terminate()


if __name__ == "__main__":
    import time
    dir_current_file = os.path.dirname(__file__)  
    dir_parent_1 = os.path.dirname(dir_current_file) 
    height_data_path = os.path.abspath(os.path.join(dir_parent_1, 'data'))
    print(dir_parent_1)
    points = np.load(os.path.join(height_data_path,'shovel_block.npy'))
    input_image_path = os.path.join(height_data_path, 'anhui_shovel_bitmap_mask.png')
    output_image_path = os.path.join(height_data_path, 'anhui_shovel_change.png')
    img = Image.open(input_image_path)
    img = img.convert('RGB')  # 转换为RGB模式以便着色
    img_array = np.array(img)  # 转换为numpy数组
    # 获取图像的宽度和高度
    width, height = img.size

    # # 打印宽度和高度
    print(f"图像的宽度: {width} 像素")
    print(f"图像的高度: {height} 像素")


    # # 转换物理坐标到像素坐标
    # x_pixels = (points[:, 0] / 0.1).astype(int)  # x轴坐标转换
    # y_pixels = (points[:, 1] / 0.1).astype(int)  # y轴坐标转换


    # 创建有效坐标掩码（防止越界）
    # valid_mask = (
    #     (x_pixels >= 0) & 
    #     (x_pixels < width) & 
    #     (y_pixels >= 0) & 
    #     (y_pixels < height)
    # )

    # # 应用掩码过滤无效坐标
    # x_valid = x_pixels[valid_mask]
    # y_valid = y_pixels[valid_mask]

    # # 在图像数组上绘制红色标记点（RGB格式）
    # img_array[y_valid, x_valid] = [255, 0, 0]  # 红色
    x_car = 729.5
    y_car = 1275.5
    data_dict = {(row[0], row[1]): row[2] for row in points}

    print(x_car, y_car)
    for i in range(-20,20):
        for j in range(-20,20):
            y = int(y_car+j)+0.5
            x = int(x_car+i)+0.5
            test_x_y = (x, y)
            if test_x_y in data_dict:
                img_array[int(y*10), int(x*10)] = [0, 255, 0]
            else:
                img_array[int(y*10), int(x*10)] = [255, 0, 0]


            
    # 保存处理后的图像
    result_img = Image.fromarray(img_array)
    
    result_img.show()


