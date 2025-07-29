
from setuptools import setup, find_packages

setup(name='maoppy',
      package_data={'maoppy': ['data/*.ini']},
      include_package_data=True,
      packages=find_packages("maoppy",exclude=['example','test']),
      requires=['numpy','scipy','astropy'],
      zip_safe=False)
