'''
Author: Mr_Yao 2316718372@qq.com
Date: 2024-05-30
Description: 授权SDK包配置
'''
from setuptools import setup, find_packages

setup(
    name="iqr_license_sdk",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "cryptography>=3.4.7",
    ],
    author="Mr_Yao",
    author_email="2316718372@qq.com",
    description="一个用于软件授权的SDK工具包",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/iqr_license_sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 