#!/usr/bin/env python
"""Setup script for mcpeepants."""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcpeepants",
    version="0.1.0",
    author="Ewvyx",
    author_email="nick@idabble.biz",
    description="Extensible MCP server library with plugin support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gizix/MCPeePants",
    project_urls={
        "Bug Tracker": "https://github.com/gizix/MCPeePants/issues",
        "Documentation": "https://github.com/gizix/MCPeePants#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=0.1.0",
        "python-dotenv>=1.0.0",
        "pytest>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcpeepants=mcpeepants.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcpeepants": ["plugins/*.py"],
    },
)
