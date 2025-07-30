# SPDX-FileCopyrightText: Copyright (c) 2025 PaddlePaddle Authors
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import subprocess
import platform
import re
import glob
from setuptools import setup
from setuptools.command.install import install

package_name = "paddlepaddle-gpu-installer"
paddle_version = "3.0.0"
paddle_base = "paddlepaddle-gpu"

# Mapping from CUDA version to corresponding PaddlePaddle source
paddle_cu_sources = {
    "12.6": "https://www.paddlepaddle.org.cn/packages/stable/cu126/",
    "11.8": "https://www.paddlepaddle.org.cn/packages/stable/cu118/",
}
default_source = paddle_cu_sources["11.8"]

def detect_cuda_version():
    """Detect CUDA version using `nvcc --version`"""
    try:
        output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
        match = re.search(r"release (\d+)\.(\d+)", output)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
    except Exception as e:
        print(f"[Warning] Failed to detect or parse nvcc output: {e}")
    return None

def select_paddle_index(cuda_version):
    """Choose PaddlePaddle package source based on CUDA version"""
    return paddle_cu_sources.get(cuda_version, default_source)

def run_pip(args, call=subprocess.check_call):
    """Run a pip command inside the Python environment"""
    env = os.environ.copy()
    env["PYTHONPATH"] = sys.exec_prefix
    return call([sys.executable, "-m", "pip"] + args, env=env)

class InstallCommand(install):
    """Custom installation command to dynamically install paddlepaddle-gpu"""
    def run(self):
        cuda_version = detect_cuda_version()
        index_url = select_paddle_index(cuda_version)

        print(f"[Info] Detected CUDA {cuda_version or 'unknown'}, using index: {index_url}")
        run_pip([
            "install",
            f"{paddle_base}=={paddle_version}",
            "-i", index_url
        ])

        super().run()

setup(
    name=package_name,
    version=paddle_version,
    description="PaddlePaddle GPU Installer with Automatic CUDA Source Selection",
    long_description=(
        "This installer automatically selects the correct paddlepaddle-gpu package source "
        "based on the detected CUDA version on your system."
    ),
    long_description_content_type="text/markdown",
    author="PaddlePaddle",
    author_email="paddle-better@baidu.com",
    maintainer="PaddlePaddle",
    maintainer_email="paddle-better@baidu.com",
    url="https://www.paddlepaddle.org.cn/",
    download_url="https://github.com/PaddlePaddle/Paddle",
    license="Apache Software License",
    packages=["paddlepaddle_gpu_installer"],  # You should have this directory with __init__.py
    include_package_data=True,
    python_requires=">=3.9,<=3.13",
    setup_requires=["wheel"],
    install_requires=[],  # Don't declare paddlepaddle-gpu here — we install it dynamically
    cmdclass={"install": InstallCommand},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="paddlepaddle gpu installer cuda deep learning",
    zip_safe=True,
)
