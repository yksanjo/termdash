#!/usr/bin/env python3
"""Setup script for TermDash."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="termdash",
    version="1.0.0",
    author="TermDash",
    description="A customizable terminal dashboard builder with beautiful widgets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/termdash/termdash",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "termdash=termdash.__main__:main",
        ],
    },
)
