'''
Created on 17.12.2020

@author: LH, BP, ED
'''
import setuptools
from iolink.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iolink",
    version=__version__,
    author="LH, BP, ED, ..",
    author_email="tmc_info@trinamic.com",
    description="Python IO-link Access Package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trinamic/iolink",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "pyserial>=3"
    ],
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    zip_safe=False,
)
