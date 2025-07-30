from setuptools import setup, find_packages
NAME = "CalculusPy"
VERSION = "0.0.2"
AUTHOR = "Mohammad Mahfuz Rahman"
AUTHOR_EMAIL = "mahfuzrahman0712@gmail.com"
DESCRIPTION = "CalculusPy is a strong python library for calculus"
GIT_REPO_URL = "https://github.com/mahfuz0712/CalculusPy.git"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=GIT_REPO_URL,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    install_requires=[
        
    ],
    include_package_data=True,
    package_data={
        
    },
)
