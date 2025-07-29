#!/usr/bin/env python
"""
Setup script for HSV - Hit Score Visualization module
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bs-hsv",
    version="1.0.0",
    author="CodeSoftGit",
    description="A Pydantic-based module for hit score vizualizer presets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeSoftGit/bs-hsv",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pillow>=9.0.0",
        "numpy>=1.20.0",
    ],
    keywords="hit score, visualization, game development, pydantic, text art, beat saber, beatsaber",
    project_urls={
        "Bug Tracker": "https://github.com/CodeSoftGit/bs-hsv/issues",
        "Documentation": "https://github.com/CodeSoftGit/bs-hsv#readme",
        "Source Code": "https://github.com/CodeSoftGit/bs-hsv",
    },
)