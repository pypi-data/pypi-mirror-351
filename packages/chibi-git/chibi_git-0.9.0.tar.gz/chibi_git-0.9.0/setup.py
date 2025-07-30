#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'chibi>=0.14.0', 'chibi_atlas>=1.1.0', 'chibi_command>=1.1.2' ]

setup(
    author="dem4ply",
    author_email='dem4ply@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="wrapper to use git in python",
    install_requires=requirements,
    license="WTFPL",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='chibi_git',
    name='chibi_git',
    packages=find_packages(include=['chibi_git', 'chibi_git.*']),
    url='https://github.com/dem4ply/chibi_git',
    version='0.9.0',
    zip_safe=False,
)
