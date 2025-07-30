#!/usr/bin/env python3
"""
Setup script for BoE ETL package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="boe-etl",
    version="1.0.0",
    author="Bank of England ETL Team",
    author_email="etl-team@bankofengland.co.uk",
    description="Pure ETL pipeline for financial document processing - extracts data without analytical assumptions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daleparr/boe-etl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "frontend": [
            "streamlit>=1.20.0",
            "plotly>=5.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "all": [
            "streamlit>=1.20.0",
            "plotly>=5.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "boe-etl=boe_etl.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "boe_etl": [
            "data/*.json",
            "data/*.yml",
            "data/*.yaml",
            "config/*.yml",
            "config/*.yaml",
        ],
    },
    keywords=[
        "etl",
        "nlp",
        "financial",
        "banking",
        "document-processing",
        "pdf-parsing",
        "earnings-calls",
        "financial-analysis",
        "text-processing",
        "data-extraction",
    ],
    project_urls={
        "Bug Reports": "https://github.com/daleparr/boe-etl/issues",
        "Source": "https://github.com/daleparr/boe-etl",
        "Documentation": "https://github.com/daleparr/boe-etl/wiki",
    },
)