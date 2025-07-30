# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='kkrobots',
    version='1.0.0',
    python_requires='>=3.7',
    packages=find_packages(),
    include_package_data=True,
    # package_data={},
    # entry_points={
    #     'console_scripts': [
    #         'kksn_server=kksn:cli',  # 注册命令行工具
    #     ],
    # },
    description='kkrobots安全爬虫守护者',
    # python3，readme文件中文报错
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Kuizi',
    author_email='123751307@qq.com',
    license='MIT',
    license_file="LICENSE.txt",
    # license_files="LICEN[CS]E*",
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Utilities'
    ]
)
