from setuptools import setup, find_packages

setup(
    name="ck3_workshop_helper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiofiles>=0.8.0",
    ],
)
