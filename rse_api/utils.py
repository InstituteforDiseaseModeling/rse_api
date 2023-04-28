import importlib
import os
from logging import getLogger
from typing import List

default_exclude = ["__init__.py"]


def dynamic_import_all(module):
    # get a handle on the module
    mdl = importlib.import_module(module)

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    return names


def load_modules(
    package_path: str, dir_path: str, exclude: List[str] = None
) -> List[str]:
    """
    Scans a specific directory path for list of possible model files. It then will import each file as part of the
    specified package_path. For example, if a directory contains the following files

    __init__.py
    package.py
    contributor.py

    And the function is called with a package_path of "test.models", load_modules will import test.models.package and
    test.models.contributor


    :param recurse: Should we recurse into other directories?
    :param package_path: Prefix to package path of directory we are scanning
    :type package_path: str
    :param dir_path: Directory to scan
    :type dir_path: str
    :param exclude: List of files to exclude. If value is None, the default list of '__init__.py' will be used
    :return: List of models loaded
    :rtype: List[str]
    """
    logger = getLogger()
    modules = []

    if exclude is None:
        exclude = default_exclude.copy()
    for root, dirs, files in os.walk(dir_path, topdown=True):
        p_path = package_path
        if root != dir_path:
            # find relative difference
            p_path += "." + os.path.relpath(root, dir_path).replace("/", ".")
        for f in files:
            if f.endswith(".py") and f not in exclude:
                name = "{}.{}".format(p_path, f.replace(".py", ""))
                importlib.import_module(name)
                modules.append(name)

    logger.debug(
        "Loaded Modules for package {} from {}: {}".format(
            package_path, dir_path, str(modules)
        )
    )
    return modules
