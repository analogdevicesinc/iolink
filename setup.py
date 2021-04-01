#!/usr/bin/env python
"""
Setup script for the `iolink` package.
"""

import setuptools

setuptools.setup(
    name='iolink',
    author='Maxim-Trinamic Software Team',
    author_email='pypi.trinamic@maximintegrated.com',
    description='IO-Link Adapter Interface',
    long_description_content_type='text/x-rst',
    url='https://github.com/trinamic/iolink',
    packages=setuptools.find_packages(),
    include_package_data=True,
    project_urls={
        'Documentation': 'https://iolink.readthedocs.io',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
)
