from numpy import get_include as np_include
from setuptools import setup, Extension

ext_modules = [
    Extension('stsci.image._combine',
              ['src/_combinemodule.c'],
              include_dirs=[np_include()],
              define_macros=[('NUMPY', '1')]),
]

setup(
    ext_modules=ext_modules,
)
