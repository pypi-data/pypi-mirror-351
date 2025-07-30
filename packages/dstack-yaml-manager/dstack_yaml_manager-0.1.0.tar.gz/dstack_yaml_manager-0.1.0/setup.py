#!/usr/bin/env python3
"""
Setup script for dstack Management Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="dstack-yaml-manager",
    version="0.1.0",
    author="dstack Management Tool Contributors",
    author_email="",
    description="A Terminal User Interface for managing dstack YAML configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dstack-mgmt/dstack-mgmt-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.38.0",
        "rich>=13.0.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dstack-yaml-manager=dstack_mgmt.cli:main",
        ],
    },
    keywords="dstack yaml tui management terminal cli",
    project_urls={
        "Bug Reports": "https://github.com/dstack-mgmt/dstack-mgmt-tool/issues",
        "Source": "https://github.com/dstack-mgmt/dstack-mgmt-tool",
        "Documentation": "https://github.com/dstack-mgmt/dstack-mgmt-tool#readme",
    },
    include_package_data=True,
    zip_safe=False,
)