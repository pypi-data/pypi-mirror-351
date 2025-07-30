"""
from distutils.core import setup
import os.path

setup(
  name = 'python-pattani',         # How you named your package folder (MyLib)
  packages = ['python-pattani'],   # Chose the same as "name"
  version = '0.0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Show Loong Pom Name Jaaa',   # Give a short description about your library
  long_description='plese read in: https://github.com/Dev-Slur/python-pattani',
  author = 'นาย ชนสิทธิ์ เจียมรัตโนภาส',                   # Type in your name
  author_email = 'chanatiff@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Dev-Slur/python-pattani',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Dev-Slur/python-pattani/archive/0.0.1.zip',    # I explain this later on
  keywords = ['LOONGTU', 'python-pattani', 'ชนสิทธิ์', 'ชนสิทธิ์ เจียมรัตโนภาส'],   # Keywords that define your package best
  install_requires=[
          'loongpom', 'pandas', 'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
"""

from setuptools import setup, find_packages

setup(
    name='pythonptn',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        #'loongpom==0.0.5',
        #'pandas==1.3.5',
        #'requests==2.31.0',
        #'pylint==2.17.7',
        #'DateTime==5.5',
        #'times==0.7',
        #'virtualenv==20.26.6',
        #'venvs==7.6.0'
    ],
    author='นาย ชนสิทธิ์ เจียมรัตโนภาส',
)