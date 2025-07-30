# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
LONGDOC = """
env3
=====================

Read .env file

https://github.com/hailiang-wang/python-env3

Usage::

    import env3

    ENV = env3.load_env(".env")
    print(ENV.get("HOME", "default"))
    env3.print_env(ENV)


"""

setup(
    name='env3',
    version='0.0.5',
    description='Read .env file',
    long_description=LONGDOC,
    author='Hai Liang Wang',
    author_email='hailiang.hl.wang@gmail.com',
    url='https://github.com/hailiang-wang/python-env3',
    license="Chunsong Public License, version 1.0",
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11'
    ],
    keywords='env',
    packages=find_packages(),
    install_requires=[
    ],
    package_data={
        'env3': [
            'LICENSE']})
