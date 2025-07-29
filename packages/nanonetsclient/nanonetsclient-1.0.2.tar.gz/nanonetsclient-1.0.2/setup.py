from setuptools import setup, find_packages

setup(
    name="nanonetsclient",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.7",
    author="Nanonets",
    author_email="support@nanonets.com",
    description="Nanonets API SDK for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nanonets/nanonets-python-sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 