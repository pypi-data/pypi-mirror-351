"""
install ulracutpro
"""

# -*- coding: utf-8 -*-
# file: setup.py
# author: JinTian
# time: 12/02/2021 12:16 PM
# Copyright 2022 JinTian. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

from setuptools import setup, find_packages

version_file = "ultracutpro/version.py"


def get_version():
    with open(version_file, "r") as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    name="ultracutpro",
    version=get_version(),
    keywords=["deep learning", "script helper", "tools"],
    description="ultracutpro: AI for cut.",
    long_description="""
      ultracutpro: AI for cut.
      """,
    license="GPL-3.0",
    packages=[
        "ultracutpro",
    ],
    author="Lucas Jin",
    author_email="test@163.com",
    platforms="any",
    install_requires=["tenacity", "pysubs2", "moviepy", "funasr_onnx"],
    entry_points={"console_scripts": ["ultracut = ultracutpro.ultracut_cli:main"]},
)
