import setuptools
from setuptools import Extension
import os

cpp_args = ['-std=c++11']

# Delay NumPy import until after pip installs build dependencies
class get_numpy_include(object):
    def __str__(self):
        import numpy
        return numpy.get_include()

sarw_spheres = Extension(
    "sarw_spheres",
    sources=["sarw_spheres.cpp"],
    language="c++",
    extra_compile_args=cpp_args,
    include_dirs=[get_numpy_include()]
)

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name="sarw_spheres",
    version="0.0.9",

    url='https://github.com/RadostW/sarw_spheres',
    author='Radost Waszkiewicz',
    author_email='radost.waszkiewicz@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    project_urls = {
      'Documentation': 'https://github.com/RadostW/sarw_spheres',
      'Source': 'https://github.com/RadostW/sarw_spheres'
    },
    license='MIT',

    description="Generate self-avoiding random walks (SARW) for spheres of given sizes.",
    ext_modules=[sarw_spheres],
    install_requires=['numpy>=2.0'],
)

