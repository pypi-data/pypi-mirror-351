from setuptools import setup, find_packages

setup(
    name="gklocal",
    version="0.1.3",
    author="Gopikrishna",
    author_email="gktrainings.tirupati@gmail.com",
    description="A simple calculator package",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "gklocal=gklocal.calculator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
