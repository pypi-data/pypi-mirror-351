# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2024/2/8 12:17
import os
import socket
import struct  # 解析simulink模型打包来的数据要用
import time
import platform
import subprocess

class Client():
    def __init__(self, Send_IP='127.0.0.1', Send_Port=25001, Receive_IP='127.0.0.1', Receive_Port=25000):
        self.send_ip = Send_IP
        self.send_port = Send_Port
        self.receive_ip = Receive_IP
        self.receive_port = Receive_Port
        self._build_client()

    def _build_client(self):
        # 发送端
        self.client_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 接收端
        self.client_receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_receive_sock.bind((self.receive_ip, self.receive_port))
    
    def send_message(self, gear, acceleration, steering_angle,continue_simulation, slope=0):
        try:
            message = struct.pack('>ddddd', gear, acceleration, steering_angle,continue_simulation, slope)
            self.client_send_sock.sendto(message, (self.send_ip, self.send_port))
            if continue_simulation == 1:
                print('进入下一控制量计算过程...')
            else:
                print('控制量已发送，等到接收下一个状态量...')
        except Exception as e:
            print(f"通信出现问题！，具体原因为{e}")

    def receive_message(self):
        """接收状态数据，持续接收直到接收到结束标志"""
        received_data = []
        chunk_size = 16  # 每次接收 16 个 double 类型数据
        buffer_size = chunk_size*8  # 设置缓冲区大小
        end_flag = [-10, -10, -10, -10]  # 结束标志是 4 个 -10

        while True:
            try:
                # 接收数据
                data, addr = self.client_receive_sock.recvfrom(buffer_size)
                if not data:  # 如果没有数据可读
                    print("没有接收到数据，退出循环")
                    break

                # 解析数据长度
                num_doubles = len(data) // 8
                #print("接收到数量：",num_doubles)

                if num_doubles % 4 != 0:
                    print(f"无效数据长度: {num_doubles} doubles")
                    return None, None

                # 解包原始数据
                fmt = f'>{num_doubles}d'
                raw = struct.unpack(fmt, data)

                # 检查是否接收到结束标志
                if list(raw[-4:]) == end_flag:  # 检查最后 4 个元素是否为结束标志
                    #print("接收到结束标志，停止接收数据")
                    received_data.extend(raw[:-4])  # 排除结束标志
                    print('状态量已接收，等待计算下一个控制量...')
                    break
                else:
                    received_data.extend(raw)  # 累积接收到的数据

            except socket.error as e:
                print(f"网络错误: {e}")
                break
            except struct.error as e:
                print(f"解包错误: {e}")
                break
            except Exception as e:
                print(f"接收错误: {e}")
                break

        # 计算接收到的状态数量
        #print("receive长度",len(received_data))
        step = len(received_data) // 4

        return received_data, step


    def send_and_receive(self, gear, acceleration, steering_angle,slope):
        try:
            message = struct.pack('>dddd', gear, acceleration, steering_angle,slope)
            print("steer", steering_angle)
            self.client_send_sock.sendto(message, (self.send_ip, self.send_port))
            t1=time.time()
            print('控制量已发送，等到接收下一个状态量...')

            data, addr = self.client_receive_sock.recvfrom(1024)
            print('状态量已接收，等待计算下一个控制量...')
            t2=time.time()
            print(f"接收到数据包，耗时{t2-t1}秒")
            if data:
                unpacked_data = struct.unpack('>dddd', data)
                return unpacked_data
        except Exception as e:
            print(f"通信出现问题！，具体原因为{e}")

    def close_sockets(self):
        self.client_send_sock.close()
        self.client_receive_sock.close()
        self.kill_matlab_processes()

    @staticmethod
    def kill_matlab_processes():
        # 获取当前操作系统类型
        os_type = platform.system()

        try:
            if os_type == "Windows":
                # 对于Windows系统，使用taskkill
                subprocess.run(["taskkill", "/F", "/IM", "MATLAB.exe"], check=True)
                print("所有MATLAB进程已被成功终止。")
            elif os_type == "Linux" or os_type == "Darwin":
                # 对于Linux和MacOS系统，使用pkill
                # MacOS系统也被视为类Unix系统，通常使用和Linux相同的命令
                # subprocess.run(["pkill", "matlab"], check=True)
                os.system("ps aux|grep 'MATLAB'|grep -v 'grep'|awk '{print $2}'|xargs kill")
                print("所有MATLAB进程已被成功终止。")
            else:
                print(f"不支持的操作系统: {os_type}")
        except subprocess.CalledProcessError as e:
            print(f"终止MATLAB进程时发生错误：{e}")





