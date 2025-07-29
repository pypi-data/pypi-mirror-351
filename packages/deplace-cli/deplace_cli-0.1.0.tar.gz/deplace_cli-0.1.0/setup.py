from setuptools import setup, find_packages

setup(
    name="deplace-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-identity>=1.15.0",
        "azure-storage-file-datalake>=12.14.1"
    ],
    entry_points={
        "console_scripts": [
            "deplacecli=deplacecli.cli:main"
        ],
    },
    author="Deplace AI",
    description="A CLI tool to access Datasets.",
)