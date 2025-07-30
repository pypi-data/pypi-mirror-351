#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='qbitnum',
    version='0.1.1',
    description='Quantum‐inspired numeric data type for probabilistic arithmetic',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
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
