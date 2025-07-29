#!/usr/bin/env python3

from setuptools import setup, find_packages
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# --- POBIERANIE WERSJI Z version.py ---
with open("version.py", "r", encoding="utf-8") as fh:
    version_line = fh.read()
    version = re.search(r'__version__\s*=\s*"([^"]+)"', version_line).group(1)

setup(
    name="git2blog",
    version=version,
    author="Developer",
    author_email="developer@example.com",
    description="Generator bloga z historii Git używający Ollama LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/py-lama/git2blog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "git2blog=git2blog:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "templates/*.css", "examples/*"],
    },
)