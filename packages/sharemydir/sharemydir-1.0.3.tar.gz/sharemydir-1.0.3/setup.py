from setuptools import setup
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="sharemydir",
    version="1.0.3",
    description="Instantly serve any folder over HTTP with zero configuration and one-click downloads.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anil Raj Rimal",
    author_email="anilrajrimal@gmail.com",
    url="https://github.com/anilrajrimal1/sharemydir",
    py_modules=["sharemydir"],
    install_requires=[
        "qrcode"
    ],
    entry_points={
        "console_scripts": [
            "sharemydir=sharemydir:main",
        ],
    },
    classifiers=[
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "License :: OSI Approved :: MIT License",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Networking",
]
,
    python_requires='>=3.9',
)
