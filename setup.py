#!/usr/bin/env python
# coding: utf-8

import distutils.core
import os.path
import sys


def get_info(module):
    "Extract distutils configuration information from a module"
 
    info = {}

    name = getattr(module, "__name__", None)
    if not name:
        name = module.__file__.split(".")[0]
    info["name"] = name

    author_info = getattr(module, "__author__", None)
    if author_info:
        # "author <author_email>" syntax expected
        info["author"] = author_info.split("<")[0].strip()
        info["author_email"] = author_info.split("<")[1].strip()[:-1]

    license = getattr(module, "__license__", None)
    if license:
        info["license"] = license

    url = getattr(module, "__url__", None)
    if url:
        info["url"] = url

    version = getattr(module, "__version__", None)
    if version:
        info["version"] = version

    doc = getattr(module, "__doc__", None)
    if doc:
        # the description is expected to be the first non-blank doc line
        lines = doc.splitlines()
        for line in lines:
            if line:
                info["description"] = line
                break

    module = getattr(module, "__file__")
    if module:
        info["py_modules"] = [os.path.basename(module).split(".")[0]]

    return info


sys.path.insert(0, "."); import zeroconf
info = get_info(zeroconf)

info["requires"] = ["sh"]

distutils.core.setup(**info)

