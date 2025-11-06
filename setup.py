"""
Setup configuration for Proto Gear
AI Agent Framework for Development Workflows
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="proto-gear",
    version="0.4.0",
    author="Proto Gear Team",
    author_email="team@protogear.dev",
    description="Proto Gear - AI Agent Framework for intelligent development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/proto-gear/proto-gear",
    project_urls={
        "Bug Tracker": "https://github.com/proto-gear/proto-gear/issues",
        "Documentation": "https://protogear.dev/docs",
        "Source Code": "https://github.com/proto-gear/proto-gear",
        "Discord": "https://discord.gg/protogear",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    packages=find_packages(where="core"),
    package_dir={"": "core"},
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0",
        "rich>=13.0",
        "questionary>=2.0",
        "pathlib>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "docs": [
            "sphinx>=6.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "full": [
            "requests>=2.31.0",
            "jinja2>=3.1.0",
            "colorama>=0.4.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "proto-gear=proto_gear:main",
            "protogear=proto_gear:main",
            "pg=proto_gear:main",  # Primary CLI command
        ],
    },
    include_package_data=True,
    package_data={
        "core": [
            "templates/*.md",
            "templates/*.yaml",
            "examples/*.yaml",
        ],
    },
    keywords=[
        "proto gear",
        "protogear",
        "ai agents",
        "agent framework",
        "ai",
        "agents",
        "automation",
        "project management",
        "orchestration",
        "development workflow",
        "sprint planning",
        "agile",
        "ticket management",
        "git workflow",
        "continuous integration",
        "software development",
        "productivity",
        "developer tools",
    ],
)