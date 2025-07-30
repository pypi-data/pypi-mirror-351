from setuptools import setup, find_packages

setup(
    name="NueroCache",
    author="Parker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "chromadb",
        "sentence-transformers",
    ],
)
