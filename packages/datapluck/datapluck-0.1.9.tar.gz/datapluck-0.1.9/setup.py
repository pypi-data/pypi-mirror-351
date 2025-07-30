from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="datapluck",
    version="0.1.9",
    author="Omar Kamali",
    author_email="pypi@datapluck.org",
    description="Export & import Hugging Face datasets to spreadsheets and various file formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "datapluck": ["credentials.json"],
    },
    entry_points={
        "console_scripts": [
            "datapluck=datapluck.main:main",
        ],
    },
    install_requires=[
        "pandas",
        "datasets",
        "pyarrow",
        "openpyxl",
        "pysqlite3",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords="huggingface datasets export csv json parquet tsv jsonl google-sheets spreadsheets google microsoft excel xls xlsx",
)
