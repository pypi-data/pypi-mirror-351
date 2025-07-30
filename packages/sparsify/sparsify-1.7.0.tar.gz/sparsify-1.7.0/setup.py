# Copyright (c) 2021 - present / Neuralmagic, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import warnings

from setuptools import setup
from setuptools.command.install import install
from typing import Tuple

class DeprecatedInstallCommand(install):
    def run(self):
        EOL_MESSAGE = """
============================================================================================
'sparsify' has reached end-of-life and is no longer supported as of June 2025.
See the README for more details: https://github.com/neuralmagic/sparsify/blob/main/README.md
============================================================================================
        """
        sys.stderr.write(EOL_MESSAGE + "\n")
        sys.exit(1)


def _setup_long_description() -> Tuple[str, str]:
    return open("README.md", "r", encoding="utf-8").read(), "text/markdown"


setup(
    name="sparsify",
    version="1.7.0",
    author="Neuralmagic, Inc.",
    author_email="support@neuralmagic.com",
    description=(
        "[DEPRECATED] Easy-to-use UI for automatically sparsifying neural networks and "
        "creating sparsification recipes for better inference performance and "
        "a smaller footprint"
    ),
    long_description=_setup_long_description()[0],
    long_description_content_type=_setup_long_description()[1],
    keywords=(
        "inference, machine learning, neural network, computer vision, nlp, cv, "
        "deep learning, torch, pytorch, tensorflow, keras, automl, sparsity, pruning, "
        "deep learning libraries, onnx, quantization"
    ),
    license="Apache",
    url="https://github.com/neuralmagic/sparsify",
    cmdclass={
        'install': DeprecatedInstallCommand,
    },
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
