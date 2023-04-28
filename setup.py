#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = dict()

for fn in ["", "_dev", "_docs", "_extras"]:
    with open("requirements{}.txt".format(fn)) as dev_requirement_file:
        requirements[
            fn.replace("_", "") if fn else "default"
        ] = dev_requirement_file.read().split("\n")

extras_require = dict(
    full=requirements["extras"] + requirements["default"],
    dev=requirements["dev"] + requirements["default"],
    docs=requirements["docs"] + requirements["dev"],
)

setup_requirements = ["pytest-runner"]
test_requirements = ["pytest"]

setup(
    author="Clinton Collins, "
    "Benoit Raybaud, "
    "Clark Kirkman IV,"
    "Zhaowei Du"
    "David Kong,"
    "Qinghua Long",
    author_email="ccollins@idmod.org, "
    "braybaud@idmod.org, "
    "ckirkman@idmod.org, "
    "zdu@idmod.org"
    "dkong@idmod.org, "
    "qlong@idmod.org",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="rse_api has common tool for standing up RESTful api services in python",
    install_requires=requirements["default"],
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    license="MIT License",
    keywords="rse_api",
    name="rse_api",
    packages=find_packages(
        include=["rse_api", "rse_api.controllers", "rse_api.tasks"], exclude=["tests"]
    ),
    setup_requires=setup_requirements,
    extras_require=extras_require,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/InstituteforDiseaseModeling/rse_api",
    version="1.0.9",
    zip_safe=False,
)
