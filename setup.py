#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements_dev.txt') as dev_requirement_file:
    dev_requirements = dev_requirement_file.read().split("\n")

extras_require={
        'full': ['dramatiq==1.4.3', 'apscheduler>=3.5.3'],
        'dev': dev_requirements
    }
requirements = [
    'flask>=1.0.x,<1.1',
    'marshmallow>2,<3'
]
setup_requirements = ['pytest-runner']
test_requirements = ['pytest']

setup(
    author="Clinton Collins, "
           "Benoit Raybaud, "
           "Clark Kirkman IV,"
           "Zhaowei Du"
           "David Kong,"
           "Qinghua Long",
    author_email='ccollins@idmod.org, '
                 'braybaud@idmod.org, '
                 'ckirkman@idmod.org, '
                 'zdu@idmod.org'
                 'dkong@idmod.org, '
                 'qlong@idmod.org',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="rse_api has common tool for standing up RESTful api services in python",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rse_api',
    name='rse_api',
    packages=find_packages(include=['rse_api', 'rse_api.controllers', 'rse_api.tasks'], exclude=["tests"]),
    setup_requires=setup_requirements,
    extras_require=extras_require,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/InstituteforDiseaseModeling/rse_api',
    version='1.0.8',
    zip_safe=False,
)
