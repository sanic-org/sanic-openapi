"""
Sanic
"""
import codecs
import os
import re

from setuptools import find_packages, setup

install_requires = ["sanic>=18.12.0", "pyyaml>=3.0.0"]

dev_requires = ["black==19.3b0", "flake8==3.7.7", "isort==4.3.19"]

doc_requires = [
    "recommonmark==0.5.0",
    "sphinx==2.1.2",
    "sphinx-rtd-theme==0.4.3",
]

test_requires = [
    "coverage==4.5.3",
    "pytest==4.6.2",
    "pytest-cov==2.7.1",
    "pytest-html==1.20.0",
    "pytest-runner==5.1",
    "tox==3.12.1",
]

project_root = os.path.dirname(os.path.abspath(__file__))

with codecs.open(
    os.path.join(project_root, "sanic_openapi", "__init__.py"), "r", "latin1"
) as fp:
    try:
        version = re.findall(
            r"^__version__ = \"([^']+)\"\r?$", fp.read(), re.M
        )[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

with open(os.path.join(project_root, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sanic-openapi",
    version=version,
    url="http://github.com/sanic-org/sanic-openapi/",
    license="MIT",
    author="Sanic Community",
    description="Easily document your Sanic API with a UI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={"sanic_openapi": ["ui/*"]},
    platforms="any",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires + test_requires + doc_requires,
        "test": test_requires,
        "doc": doc_requires,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
