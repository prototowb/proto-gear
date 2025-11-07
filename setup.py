"""
Setup configuration for Proto Gear
"""

from setuptools import setup, find_packages

setup(
    packages=find_packages(where="core"),
    package_dir={"": "core"},
    package_data={
        "proto_gear_pkg": [
            "*.md",
            "*.yaml",
            "*.yml",
            "capabilities/**/*.md",
        ],
    },
    include_package_data=True,
)
