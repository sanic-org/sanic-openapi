"""
Sanic
"""
import codecs
import os
import re
from setuptools import setup


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'sanic_openapi', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name='sanic-openapi',
    version=version,
    url='http://github.com/channelcat/sanic/',
    license='MIT',
    author='Channel Cat',
    author_email='channelcat@gmail.com',
    description='OpenAPI support for Sanic',
    packages=['sanic_openapi'],
    package_data={'sanic_openapi': ['ui/*']},
    platforms='any',
    install_requires=[
        'sanic>=0.6.0',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
