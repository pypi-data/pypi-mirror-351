"""Setup file for the ARL package."""

import os
from setuptools import find_packages, setup


# Get the version from palaestrai.__version__ without executing the module:
version = {}
with open(
    os.path.join(os.path.dirname(__file__), "src", "harl", "version.py")
) as fp:
    exec(fp.read(), version)
VERSION = version["__version__"]

with open("VERSION", "w") as fp:
    fp.write(VERSION)

with open("README.rst") as freader:
    README = freader.read()

setup(
    name="palaestrai-agents",
    version=VERSION,
    description="Implementation of src-algorithms for ARL.",
    long_description=README,
    author="Eric MSP Veith <eric.veith@offis.de>",
    author_email="eric.veith@offis.de",
    python_requires=">=3.10.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "torch>=2.1.0",
        "numpy >=1.18.5, <2.0",
    ],
    extras_require={
        "dev": [
            "tox>=3.23.0",
            "robotframework >= 4.0.0",
            "pytest>=6.2.4",
            "pytest-cov",
            "coverage",
            "black==24.1.0",
            "mypy",
            "ipython",
            "plotly",
        ]
    },
    license="LGPL",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
