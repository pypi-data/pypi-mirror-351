# setup.py
#
# Setup Instructions for MML Library
# From MML Library by Nathmath

from setuptools import setup, find_packages

setup(
    name="mml-pypi",
    version="0.0.5",
    packages=find_packages(),
    install_requires=["numpy", "scipy", "torch", "pandas", "matplotlib"],
    author="DOF Studio",
    author_email="dof.hbx@gmail.com",
    description="My Machine Learning (MML) Library, a high performance machine learning and deep learning framework coding from scratch (pure Python) with hybrid backend support (`numpy` or `torch`).. Write `import mml` to use it.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dof-studio/MML/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
