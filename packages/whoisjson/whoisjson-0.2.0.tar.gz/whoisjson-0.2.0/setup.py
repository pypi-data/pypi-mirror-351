from setuptools import setup, find_packages

setup(
    name="whoisjson",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="Whoisjson",
    author_email="postmaster@whoisjson.com",
    description="A Python client for the whois-json API service",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://whoisjson.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
) 