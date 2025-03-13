#!/usr/bin/python3 -O
#
# Copyright 2025 Daniel Balparda (balparda@gmail.com)
# GNU General Public License v3 (http://www.gnu.org/licenses/gpl-3.0.txt)
#
"""Setup."""

import pathlib

import setuptools


def _ReadRequirements() -> list[str]:
  """Read dependencies from requirements.txt."""
  req_file: pathlib.Path = pathlib.Path(__file__).parent / 'requirements.txt'
  if not req_file.is_file():
    return []
  return req_file.read_text().splitlines()


setuptools.setup(
    name='baselib',
    version='1.1.1',
    description='A base library for various utilities',
    author='Daniel Balparda',
    author_email='balparda@gmail.com',
    license='GPL-3.0-or-later',
    packages=setuptools.find_packages(
        include=['baselib', 'baselib.*']
    ),
    include_package_data=True,
    install_requires=_ReadRequirements(),
    python_requires='>=3.9',
    url='https://github.com/balparda/baselib',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
