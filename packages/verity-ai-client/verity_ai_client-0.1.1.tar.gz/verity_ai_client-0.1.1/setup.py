#!/usr/bin/env python3
"""
Setup script for Verity AI Python Client
"""

from pathlib import Path
from setuptools import setup, find_packages

# Get the directory containing this setup.py file
here = Path(__file__).parent.absolute()

# Read the README file
readme_file = here / "README.md"
with open(readme_file, "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
requirements = [
    "urllib3>=2.1.0,<3.0.0",
    "python-dateutil>=2.8.2",
    "pydantic>=2.0.0",
    "typing-extensions>=4.7.1"
]

# Find packages in the current directory
packages = find_packages(include=["verity_ai_pyc*"])

setup(
    name="verity-ai-client",
    version="0.1.1",
    description="Official Python client for Verity AI - Comprehensive API service for unstructured and structured RAG generation, file management, and AI interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Verity Labs",
    author_email="support@veritylabs.ai",
    maintainer="Verity Labs",
    maintainer_email="support@veritylabs.ai",
    url="https://veritylabs.ai",
    project_urls={
        "Homepage": "https://veritylabs.ai",
        "Documentation": "https://docs.veritylabs.ai",
        "Repository": "https://github.com/veritylabs/verity-ai-python-client",
        "Bug Tracker": "https://github.com/veritylabs/verity-ai-python-client/issues",
        "Changelog": "https://github.com/veritylabs/verity-ai-python-client/blob/main/CHANGELOG.md",
    },
    packages=packages,
    package_data={
        "verity_ai_pyc": ["py.typed"],
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.2.1",
            "pytest-cov>=2.8.1",
            "tox>=3.9.0",
            "flake8>=4.0.0",
            "types-python-dateutil>=2.8.19.14",
            "mypy>=1.5",
            "black>=22.0.0",
            "isort>=5.0.0"
        ],
        "examples": [
            "python-dotenv>=1.0.0"
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Typing :: Typed"
    ],
    keywords=[
        "verity-ai", 
        "rag", 
        "retrieval-augmented-generation", 
        "ai", 
        "machine-learning", 
        "nlp", 
        "document-processing", 
        "knowledge-base", 
        "openapi", 
        "api-client"
    ],
    license="MIT",
    zip_safe=False,
) 