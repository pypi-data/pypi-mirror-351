from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

d = {}
with open("deepstkit/_version.py") as f:
    exec(f.read(), d)

setup(
    name="deepstkit",
    version=d["__version__"],
    description="""Identification of spatial domains in spatial transcriptomics by deep learning.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="XU CHANG",
    packages=find_packages(include=["deepstkit"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    license="MIT",
    url="https://github.com/EsdenRun/DeepST",
    python_requires=">=3.9",
)
