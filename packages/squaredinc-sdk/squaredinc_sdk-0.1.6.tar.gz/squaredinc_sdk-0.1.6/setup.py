from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="squaredinc-sdk",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        "requests>=2.32.0",  # Use newer version of requests compatible with Python 3.13
    ],
    author="Squared Inc.",
    author_email="sdk@squaredinc.co",
    description="Squared Inc. SDK for payment processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="payments, squaredinc, sdk",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
