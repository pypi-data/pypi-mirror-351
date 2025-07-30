# setup.py
#
# Setup Instructions for VVC Library
# From VVC Library by dof-studio

from setuptools import setup, find_packages

setup(
    name="vvc",
    version="0.0.0",
    packages=find_packages(),
    install_requires=["numpy"],
    author="DOF Studio",
    author_email="dof.hbx@gmail.com",
    description="Viewable Version Control (vvc) library and software. Inspired by air crashes.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dof-studio/VVC/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
