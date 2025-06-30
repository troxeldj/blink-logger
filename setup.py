#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
  requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
  name="blink-logger",
  version="0.1.0",
  author="github.com/troxeldj",
  description="A custom Python logging library built from scratch",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/troxeldj/blink-logger",
  packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Logging",
  ],
  python_requires=">=3.8",
  install_requires=[],
  extras_require={
    "dev": requirements,
    "test": ["pytest>=6.0"],
  },
  entry_points={
    "console_scripts": [
      # Add any CLI commands here if needed in the future
    ],
  },
  include_package_data=True,
  zip_safe=False,
)
