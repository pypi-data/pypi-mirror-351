from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="espressonow",
    version="0.1.0",
    author="ethanqcarter",
    author_email="ethanqcarter@gmail.com",
    description="A CLI tool to find specialty coffee shops near you",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ethanqcarter/EspressoNow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "geocoder>=1.38.1",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "espresso=espressonow.cli:main",
        ],
    },
    keywords="coffee, cli, places, api, specialty, coffee shops",
    project_urls={
        "Bug Reports": "https://github.com/ethanqcarter/EspressoNow/issues",
        "Source": "https://github.com/ethanqcarter/EspressoNow",
    },
) 