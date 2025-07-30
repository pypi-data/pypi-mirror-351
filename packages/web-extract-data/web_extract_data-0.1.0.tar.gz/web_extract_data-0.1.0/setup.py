from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web-extract-data",
    version="0.1.0",
    author="InstantAPI.ai",
    author_email="help@instantapi.ai",
    description="A Python package for extracting structured data from websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://web.instantapi.ai/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="web scraping, data extraction, html parsing, structured data, api client",
    python_requires=">=3.9",
    install_requires=[
        "requests",
    ],
    project_urls={
        "Documentation": "https://web.instantapi.ai/documentation/",
        "Source": "https://github.com/zeeb0tt/pip-web-extract-data",
        "Bug Reports": "https://github.com/zeeb0tt/pip-web-extract-data/issues",
    },
)
