#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from package
def read_version():
    version_file = os.path.join("pbt", "__version__.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            exec(f.read())
            return locals()["__version__"]
    return "0.1.0"

setup(
    name="pbt-cli",
    version=read_version(),
    author_email="saipy252@gmail.com",
    description="Infrastructure-grade prompt engineering for AI teams working across LLMs",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/prompt-build-tool/pbt",
    project_urls={
        "Bug Tracker": "https://github.com/prompt-build-tool/pbt/issues",
        "Documentation": "https://github.com/prompt-build-tool/pbt/blob/main/README.md",
        "Source Code": "https://github.com/prompt-build-tool/pbt",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        
        # LLM providers
        "anthropic>=0.7.8",
        "openai>=1.3.7",
        
        # Database and auth
        "supabase>=2.0.2",
        
        # Server dependencies (optional)
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        
        # Export functionality
        "markdownify>=0.11.6",
        
        # Security
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
    extras_require={
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "aiohttp>=3.9.0",
            "websockets>=12.0",
            "aiofiles>=23.2.1",
        ],
        "server": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "stripe>=7.8.0",
            "python-multipart>=0.0.6",
            "email-validator>=2.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.22.0",
        ],
        "all": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "stripe>=7.8.0",
            "python-multipart>=0.0.6",
            "email-validator>=2.1.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pbt=pbt.cli.main:app",
            "prompt-build-tool=pbt.cli.main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "pbt": [
            "templates/*.yaml",
            "templates/*.sql",
            "static/*",
            "config/*.json",
            "web/static/*",
            "web/static/css/*",
            "web/static/js/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "prompt engineering",
        "llm",
        "ai",
        "machine learning",
        "claude",
        "openai",
        "gpt",
        "testing",
        "evaluation",
        "automation",
    ],
)