# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='mmblelink',
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["python-dateutil", "decocare", "gattlib"],
    scripts = [
      'bin/mmblelink'
    , 'bin/mmblelink-send.py'
    ]
)
