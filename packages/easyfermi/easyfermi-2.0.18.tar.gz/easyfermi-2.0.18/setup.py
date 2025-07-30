
  
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '2.0.18'
DESCRIPTION = 'The easiest way to analyze Fermi-LAT data'
LONG_DESCRIPTION = 'A GUI that allows to measure the flux, create light curves, SEDs, and TS maps for Fermi-LAT data.'

# Setting up
setup(
    name="easyfermi",
    version=VERSION,
    author="Raniere de Menezes",
    author_email="<easyfermi@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    #install_requires=['PyQt5', 'astropy'],
    keywords=['python', 'fermi', 'GUI', 'graphical interface', 'easyfermi', 'gamma-rays'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
    ],
    include_package_data=True,
    package_data={'': ['resources/images/*.png','resources/ebl/*.fits.gz']},
)
