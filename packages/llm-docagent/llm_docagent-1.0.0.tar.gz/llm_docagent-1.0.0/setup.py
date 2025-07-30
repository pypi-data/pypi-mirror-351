#!/usr/bin/env python3
"""
Setup configuration for DocAgent - AI-powered documentation generator
"""

from setuptools  import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="docagent",
    version="2.0.0",
    author="Ansh Tyagi",
    author_email="anshtyagi314159@gmail.com",
    description="AI-powered documentation generator for code projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com//docagent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "twine>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docagent=docagent.cli:main",
        ],
    },
    keywords="documentation ai llm openai huggingface ollama groq code-analysis",
    project_urls={
        "Bug Reports": "https://github.com/Anshtyagi1729//DocAgent/issues",
        "Source": "https://github.com/Anshtyagi1729//DocAgent",
        "Documentation": "https://github.com/Anshtyagi1729//DocAgent#readme",
    },
    include_package_data=True,
    zip_safe=False,
)