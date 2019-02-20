#!/usr/bin/env python

import os

import setuptools

NAME = 'rust_crate_vendor'


def open_file(name):
    return open(os.path.join(os.path.dirname(__file__), name))


__version__ = None
for line in open_file(NAME + '.py'):
    if line.startswith('__version__'):
        exec(line)
        break

setuptools.setup(
    name=NAME,
    version=__version__,
    packages=setuptools.find_packages(exclude=['tests']),
    py_modules=[NAME],
    entry_points={
        'console_scripts': [
            'rust_crate_vendor=rust_crate_vendor:main',
        ],
    },
    description='``rust_crate_vendor``, an tool to expand Rust crates.',
    long_description=open_file('README.rst').read(),
    keywords='rust crate expand cargo vendor',
    url='https://github.com/drmikehenry/rust_crate_vendor',
    author='Michael Henry',
    author_email='drmikehenry@drmikehenry.com',
    license='MIT',
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
