"""
Setup configuration for Agent Framework
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
    name="agent-framework",
    version="1.0.0",
    author="Agent Framework Team",
    author_email="team@agent-framework.dev",
    description="Adaptive AI agent orchestration framework for autonomous project management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agent-framework/agent-framework",
    project_urls={
        "Bug Tracker": "https://github.com/agent-framework/agent-framework/issues",
        "Documentation": "https://agent-framework.dev/docs",
        "Source Code": "https://github.com/agent-framework/agent-framework",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="core"),
    package_dir={"": "core"},
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0",
        "rich>=13.0",
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
    },
    entry_points={
        "console_scripts": [
            "agent-framework=agent_framework.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agent_framework": [
            "templates/*.md",
            "templates/*.yaml",
            "examples/*.yaml",
        ],
    },
    keywords=[
        "ai",
        "agents", 
        "automation",
        "project management",
        "orchestration",
        "framework",
        "development workflow",
        "sprint planning",
        "agile",
    ],
)