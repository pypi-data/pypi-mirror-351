from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pnt",
    version="0.0.6",
    author="Jacob Rohde",
    author_email="jarohde1@gmail.com",
    description="A simple tool for generating and analyzing bibliometric citation network data from Pubmed.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jarohde/pnt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=['networkx', 'pandas', 'numpy', 'metapub', 'PyMuPDF'],
    license="MIT"
)
