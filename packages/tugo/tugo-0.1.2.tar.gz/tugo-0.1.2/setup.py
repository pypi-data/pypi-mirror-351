from setuptools import setup, find_packages

setup(
    name='tugo',  # 项目名称
    version='0.1.2',  # 项目版本
    packages=find_packages(),  # 自动查找包
    install_requires=[
        'anyio==4.9.0',
        'flet==0.27.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
