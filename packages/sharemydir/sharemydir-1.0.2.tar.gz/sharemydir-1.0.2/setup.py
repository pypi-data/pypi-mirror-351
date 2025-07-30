from setuptools import setup

setup(
    name="sharemydir",
    version="1.0.2",
    description="Instantly serve any folder over HTTP with zero configuration and one-click downloads.",
    long_description="A tiny cross-platform Python CLI tool to instantly serve any folder over HTTP. Supports local IP discovery, QR code display for mobile access, folder downloads as ZIP files, and a user-friendly web UI.",
    long_description_content_type="text/plain",
    author="Anil Raj Rimal",
    author_email="anilrajrimal@gmail.com",
    readme = "README.md",
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
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires='>=3.9',
)
