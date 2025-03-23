from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="phenoage-toolkit",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A toolkit for phenotypic age calculation, percentile ranking, and intervention simulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/phenoage-toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "scipy>=1.5.0",
    ],
    entry_points={
        "console_scripts": [
            "phenoage=phenoage_toolkit.cli:main",
        ],
    },
)
