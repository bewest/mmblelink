# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='meowlink',
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["python-dateutil", "decocare"],
    scripts = [
      'bin/meowlink'
    , 'bin/meowlink-send.py'
    ]
)
