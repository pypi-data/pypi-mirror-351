#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='qbitnum',
    version='0.1.0',
    description='Quantum‐inspired numeric data type for probabilistic arithmetic',
    author='Maurya Allimuthu',
    author_email='catchmaurya@gmail.com',
    url='https://github.com/catchmaurya/qbitnum',
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    install_requires=[],
    license='MIT',
    keywords='quantum qubit probabilistic arithmetic',
)
