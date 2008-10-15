# -*- coding: iso-8859-1 -*-
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(
    name = "test2to3",
    version = "1.0",
    description = "2to3 distutils test package",
    author = "Martin v. L�wis",
    author_email = "python-dev@python.org",
    license = "PSF license",
    packages = ["test2to3"],
    cmdclass = {'build_py':build_py}
)
