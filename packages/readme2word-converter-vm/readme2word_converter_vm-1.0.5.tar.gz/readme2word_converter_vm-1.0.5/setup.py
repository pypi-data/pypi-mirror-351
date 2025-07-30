#!/usr/bin/env python3
"""
Setup script for README to Word Converter
"""

import os
import re

from setuptools import find_packages, setup


# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read version from __init__.py
def get_version():
    with open("readme2word/__init__.py", "r", encoding="utf-8") as fh:
        content = fh.read()
        match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", content)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


setup(
    name="readme2word-converter-vm",
    version=get_version(),
    author="Vishal Mishra",
    author_email="vishal@example.com",
    description="Convert README.md files to professional Word documents with Mermaid diagram support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vishalm/readme2readall",
    project_urls={
        "Bug Tracker": "https://github.com/vishalm/readme2readall/issues",
        "Documentation": "https://github.com/vishalm/readme2readall#readme",
        "Source Code": "https://github.com/vishalm/readme2readall",
        "Changelog": "https://github.com/vishalm/readme2readall/releases",
    },
    packages=find_packages(exclude=["tests*", "infra*", "output*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Documentation",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docker": [
            "docker>=6.0.0",
        ],
        "kubernetes": [
            "kubernetes>=25.0.0",
            "pyyaml>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "readme2word=readme2word.cli:main",
            "readme2word-web=readme2word.web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "readme2word": [
            "templates/*.html",
            "static/*",
            "config/*.toml",
        ],
    },
    keywords=[
        "readme",
        "markdown",
        "word",
        "docx",
        "converter",
        "mermaid",
        "diagrams",
        "documentation",
        "streamlit",
        "office",
        "document",
        "export",
        "technical-writing",
    ],
    zip_safe=False,
)
