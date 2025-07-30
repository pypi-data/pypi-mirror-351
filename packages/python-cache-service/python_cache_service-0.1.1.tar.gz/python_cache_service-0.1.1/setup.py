from setuptools import setup, find_packages

import cache
import test_cache

setup(
    name="cache-cache_service",
    version="0.1.0",
    author="Johannes Broch-Due",
    author_email="johannesbrochdue@gmail.com",
    description="Simple namespaced cache cache_service using Redis",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Johannesbrochdue/python-cache-service",
    packages=find_packages(include=["cache", "cache.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "redis",
        "fakeredis",
    ],
)