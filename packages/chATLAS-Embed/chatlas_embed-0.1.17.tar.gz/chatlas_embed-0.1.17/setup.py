from setuptools import setup, find_packages

setup(
    name="chATLAS_Embed",
    version="0.1.17",
    description="A modular Python package for efficient embedding workflows and PostgreSQL-based vector store management with parent-child relationships.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ben Elliot",
    author_email="Ben.Elliot27@outlook.com",
    url="https://gitlab.cern.ch/belliot/chatlas-packages/",
    project_urls={
        "Documentation": "https://chatlas-packages.docs.cern.ch/chATLAS_Embed/"
    },
    packages=find_packages(),
    install_requires=[
        "langchain~=0.3.3",
        "beautifulsoup4~=4.12.2",
        "tqdm~=4.66.5",
        "SQLAlchemy~=2.0.35",
        "spacy~=3.7.4",
        "pydantic~=2.9.2",
        "sentence_transformers~=3.2.0",
        "pathlib",
        "aiofiles~=23.2.1",
        "aiohttp~=3.10.10",
        "psycopg2-binary~=2.9.10",
        "tiktoken~=0.8.0",
        "langchain_core",
        "datasets~=3.0.1",
        "dataclasses",
        "numpy~=1.26.4",
        "requests~=2.32.3",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
