#!/usr/bin/env python
import importlib
import io
import os
import sys

try:
    from setuptools import find_packages, setup
except ImportError:
    raise ImportError(
        "'setuptools' is required but not installed. To install it, "
        "follow the instructions at "
        "https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py"
    )


def read(*filenames, **kwargs):
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


root = os.path.dirname(os.path.realpath(__file__))
pkg_spec = importlib.util.spec_from_file_location(
    "version", os.path.join(root, "nengo_gui", "version.py")
)
pkg_module = importlib.util.module_from_spec(pkg_spec)
sys.modules["version"] = pkg_module
pkg_spec.loader.exec_module(pkg_module)

setup(
    name="nengo-gui",
    version=pkg_module.version,
    author="Applied Brain Research",
    author_email="info@appliedbrainresearch.com",
    packages=find_packages(),
    scripts=[],
    include_package_data=True,
    url="https://github.com/nengo/nengo-gui",
    license="GNU General Public License, version 2",
    description="Web-based GUI for building and visualizing Nengo models.",
    long_description=read("README.rst", "CHANGES.rst"),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nengo_gui = nengo_gui:old_main",
            "nengo = nengo_gui:main",
        ]
    },
    install_requires=[
        "nengo>=2.6.0",
    ],
    tests_require=[
        "pytest",
        "selenium",
    ],
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
