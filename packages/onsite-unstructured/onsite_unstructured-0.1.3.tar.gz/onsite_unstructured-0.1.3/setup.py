import os
import setuptools
from setuptools import setup, find_packages

# 允许setup.py在任何路径下执行
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name="onsite_unstructured",  # 库名
    version="0.1.3",  # 版本号
    author="kaiwen",  # 作者
    author_email="xhh666@sjtu.edu.cn",  # 作者邮箱
    description="A small example package",  # 简介
    long_description="long_description",  # 详细描述
    long_description_content_type="text/markdown",  # 描述语法
    url="https://github.com/pypa/sampleproject",  # 项目主页
    packages=find_packages(),
    package_data={
        "onsite_unstructured": [
            "onsite-unstructured/data/*.npy",
            "onsite-unstructured/VehicleModel_dll/*.so",
            "onsite-unstructured/VehicleModel_dll/*.dll"
        ]
    },
    include_package_data=True,  # 激活 MANIFEST.in 文件
    classifiers=[  # 指定库的分类器
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[  # 依赖库
        'pyautogui',
        'Django >= 1.11',
    ],
    python_requires='>=3.6',
)