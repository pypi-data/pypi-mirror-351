# -*- coding: utf-8 -*-
# module setup.py
#
# Copyright (c) 2015-2024  Cogniteva SAS
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ---------------------------------------------------------------------------
# Minimal port of the ELG functionality from Cogniteva's Wolfish Record
# Linkage (WRL) Library
# ---------------------------------------------------------------------------
from setuptools import setup, find_packages
import os

# Function to find package data files
def find_package_data(package, directory):
    paths = []
    for (path, directories, filenames) in os.walk(os.path.join(package, directory)):
        for filename in filenames:
            paths.append(os.path.relpath(os.path.join(path, filename), package))
    return paths

# Define the package data
package_data = {
  'elglib': find_package_data('elglib', '.')
}

setup(
    name='elglib',
    version='1.0.0',
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    # Add additional metadata if needed
    author='martinec',
    author_email='martinec<at>cogniteva.fr',
    description='A minimal ELG module.',
    url='https://cogniteva.fr',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
