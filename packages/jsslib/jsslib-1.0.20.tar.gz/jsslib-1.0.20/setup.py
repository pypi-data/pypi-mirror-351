#!/usr/bin/env python
from setuptools import setup

# See setup.cfg for configuration.
setup(
    package_data={
        'jsslib': ['libjsslib.dylib', 'libjsslib.so', 'jsslib_x64.dll', 'jsslib_arm64.dll', 'jsslib.py', 'base.lex'],
    }
)

