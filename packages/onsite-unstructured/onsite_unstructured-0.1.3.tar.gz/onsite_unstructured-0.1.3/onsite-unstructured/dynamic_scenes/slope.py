import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.io as sio  # 用于加载 .mat 文件
import time 

# 获取当前脚本所在的文件夹路径
current_folder = os.path.dirname(os.path.abspath(__file__))
# 获取上一级目录的路径
parent_folder = os.path.dirname(current_folder)
# 构造目标文件夹路径（例如 data 文件夹）
data_folder = os.path.join(parent_folder, 'kinetic_model')
# 构造文件的完整路径
vx_path = os.path.join(data_folder, 'vx.mat')
vy_path = os.path.join(data_folder, 'vy.mat')
grid_path = os.path.join(data_folder, 'grid.mat')

# 加载文件
vx = sio.loadmat(vx_path)
vy = sio.loadmat(vy_path)
grid = sio.loadmat(grid_path)

vx=vx['vx']
vy=vy['vy']
grid=grid['grid']



class GradientCalculator:
    def __init__(self, grid, vx, vy):
        self.grid = grid
        self.vx = vx
        self.vy = vy
        self.x_min = np.min(grid[:,:,0])
        self.y_min = np.min(grid[:,:,1])
        self.dx = 0.1
        self.dy = 0.1
        
    def get_gradient(self, x, y, theta):
        """带边界保护的梯度查询"""
        x = np.float64(x)
        y = np.float64(y)
        theta = np.float64(theta)
        
        # 计算安全索引
        i = int(np.clip(np.round((x - self.x_min)/self.dx), 
                      0, self.vx.shape[0]-1))
        j = int(np.clip(np.round((y - self.y_min)/self.dy), 
                      0, self.vx.shape[1]-1))
        dx_val = self.vx[i,j]
        dy_val = self.vy[i,j]
        return dx_val*np.cos(theta) + dy_val*np.sin(theta)



x = 1034.6#米
y = 542.7
theta = -1.566#度

calculator = GradientCalculator(grid,vx,vy)
t1 = time.time()
print("梯度值 ({:.2f},{:.2f},{:.2f}):".format(x, y, theta), 
            calculator.get_gradient(x, y, theta))

t2 = time.time()
print(t2-t1)