#!/usr/bin/env python3
"""
Setup script for Constant Contact Google Sheets Unsubscriber
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="constant-contact-sheets-unsubscriber",
    version="1.0.0",
    author="Julio Salvat",
    author_email="code@juliosalvat.com",
    description="Automatically unsubscribe emails from Constant Contact using Google Sheets integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juliosalvat/constant-contact-sheets-unsubscriber",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cc-unsubscriber=constant_contact_unsubscriber.cli:main",
            "cc-monitor=constant_contact_unsubscriber.monitor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="constant-contact email unsubscribe google-sheets automation",
    project_urls={
        "Bug Reports": "https://github.com/juliosalvat/constant-contact-sheets-unsubscriber/issues",
        "Source": "https://github.com/juliosalvat/constant-contact-sheets-unsubscriber",
        "Documentation": "https://github.com/juliosalvat/constant-contact-sheets-unsubscriber#readme",
    },
) 