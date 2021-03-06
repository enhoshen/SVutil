#!/usr/bin/env python3
from setuptools import setup
from glob import glob
from sysconfig import get_config_var

ext_args = {
    # The second libraries argument is necessary for python 3.4
    'libraries': [ "python" + get_config_var('LDVERSION'),],
    'extra_compile_args': ['--std=c++11'],
}
setup(
     name='SVutil'
    ,version='0.9'
    #,description='Python Distribution Utilities'
    ,author='En-Ho Shen'
    ,author_email='enhoshen@media.ee.ntu.edu.tw'
    ,url='https://github.com/enhoshen/SVutil'
    ,packages=setuptools.find_packages()
    ,install_requires=[
         'colorama'
        ,'xlsxwriter'
        ,'nicotb @ git+https://github.com/johnjohnlin/nicotb'
        ]
    ,package_dir={
         'SVutil': 'SVutil'
        }
    ,ext_modules=[
        ]
    ,package_data={
         'SVutil.gen': ['drawio_block_ex.txt, *.md']
        ,'Svutil.sim': ['*.md', 'mynWave.conf', 'mynovas.rc']
        }
    ,scripts = [
         'script/Gen.py'
        ]
    ,
)
