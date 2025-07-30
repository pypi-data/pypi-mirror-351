from setuptools import setup, find_packages

setup(
    name="desync-data",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "desync_search",
        "beautifulsoup4",
    ],
    author="Jackson Ballow",
    description="Utility tools for Desync AI users",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python :: 3"],
    python_requires=">=3.7",
)
