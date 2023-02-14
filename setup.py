import os
from setuptools import setup, find_packages


def read(*paths):
    """Reae the contents of a text file safely.
    >>> read("dundie", "VERSION")
    '0.1.0'
    >>> read(README.md)
    ...
    """
    rootpath = os.path.dirname(__file__)
    filepath = os.path.join(rootpath, *paths)
    with open(filepath) as f:
        return f.read().strip()


def read_requirements(path):
    """Return a list of requirements from a text file"""
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(("#", "git", '"', '-'))
    ]

setup(
    name="trade",
    version="0.1.0",
    description="A quantitative trade training",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Rogerio Rodrigues",
    python_requires=">=3.10.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "trade = trade.__main__:main"
        ]
    },
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "test": read_requirements("requirements.test.txt"),
        "dev":  read_requirements("requirements.dev.txt")
    }
)
