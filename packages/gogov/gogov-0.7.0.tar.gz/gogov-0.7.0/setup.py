from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="gogov",
    packages=["gogov"],
    entry_points={
        "console_scripts": ["gogov=gogov.__init__:main"],
    },
    version="0.7.0",
    description="Unofficial API Client for GoGov CRM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel J. Dufour",
    author_email="daniel.j.dufour@gmail.com",
    url="https://github.com/officeofperformancemanagement/gogov",
    download_url="https://github.com/officeofperformancemanagement/gogov/tarball/download",
    keywords=["crm", "data", "gogov", "python"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    install_requires=["flatmate", "requests"],
)
