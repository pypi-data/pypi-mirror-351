#!/usr/bin/env python3
"""
BonicBot Python Library Setup with Optional GUI
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bonicbot",
    version="1.0.2",
    author="Shahir abdulla",  # Replace with your name
    author_email="shahir@autobonics.com",  # Replace with your email
    description="Python library for controlling BonicBot humanoid robot via serial communication",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Autobonics/bonicbot",  # Replace with your GitHub repo
    project_urls={
        "Bug Tracker": "https://github.com/Autobonics/bonicbot/issues",
        "Documentation": "https://github.com/Autobonics/bonicbot/docs",
        "Source Code": "https://github.com/Autobonics/bonicbot",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "gui": [],  # tkinter is built-in, no extra dependencies needed
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "bonicbot-gui=bonicbot.gui:run_servo_controller [gui]",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "robot", "robotics", "servo", "control", "serial", "communication",
        "humanoid", "bonicbot", "hardware", "automation"
    ],
)