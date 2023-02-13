from setuptools import setup, find_packages


setup(
    name="trade",
    version="0.1.0",
    description="A quantitative trade training",
    author="Rogerio Rodrigues", 
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "trade = trade.__main__:main"
        ]
    }
)
