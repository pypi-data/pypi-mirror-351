from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smartdriveduo",
    version="1.0.0",
    author="James Wilson",
    author_email="james@james.baby",
    description="A Python library for controlling the Cytron SmartDriveDuo 30A motor controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sssynk/smartdriveduo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyserial>=3.5",
    ],
    keywords="motor, controller, cytron, smartdriveduo, robotics, hardware",
    project_urls={
        "Bug Reports": "https://github.com/sssynk/smartdriveduo/issues",
        "Source": "https://github.com/sssynk/smartdriveduo",
    },
) 