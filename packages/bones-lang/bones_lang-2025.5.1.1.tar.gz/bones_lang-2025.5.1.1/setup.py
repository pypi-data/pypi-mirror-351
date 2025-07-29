from setuptools import setup, find_packages
from distutils.core import Extension

# read the contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = "2025.05.01.1"

# print(find_packages())
# https://stackoverflow.com/questions/27281785/python-setup-py-how-to-set-the-path-for-the-generated-so



setup(
  name='bones-lang',
  packages=[
    'bones',
    'bones.kernel',
    'bones.lang',
  ],
  # ext_modules=[Extension("bones.jones", ["./bones/c/jones/__jones.c"])],
  # package_dir = {'': 'core'},
  # namespace_packages=['coppertop_'],
  version=version,
  install_requires=[
    'coppertop-bones >= 2025.05.01.1',
    'numpy >= 1.17.3'
  ],
  python_requires='>=3.11',
  license='Apache',
  description = 'Python implementation of the bones language',
  long_description_content_type='text/markdown',
  long_description=long_description,
  author = 'David Briant',
  author_email = 'dangermouseb@forwarding.cc',
  url = 'https://github.com/coppertop-bones/bones',
  download_url = '',
  keywords = ['multiple', 'dispatch', 'piping', 'pipeline', 'pipe', 'functional', 'multimethods', 'multidispatch',
    'functools', 'lambda', 'curry', 'currying'],
  include_package_data=True,
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Topic :: Utilities',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.11',
  ],
  zip_safe=False,
)

# https://autopilot-docs.readthedocs.io/en/latest/license_list.html
# https://pypi.org/classifiers/
