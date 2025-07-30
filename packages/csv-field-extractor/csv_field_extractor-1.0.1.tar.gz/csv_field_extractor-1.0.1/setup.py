from setuptools import setup, find_packages

setup(
    name="csv-field-extractor",
    version="1.0.1",
    author="hackjustin",
    author_email="badsign@gmail.com",
    description="A simple utility to extract specific fields from CSV files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hackjustin/csv-field-extractor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "csv-extract=csv_field_extractor:main",
        ],
    },
)