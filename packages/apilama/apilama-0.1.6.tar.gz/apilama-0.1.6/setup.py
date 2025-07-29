#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="apilama",
    version="0.1.6",
    author="Tom Sapletta",
    author_email="info@pylama.dev",
    description="Backend API service for the PyLama ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/py-lama/apilama",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "apilama=apilama.cli:main",
        ],
    },
)
