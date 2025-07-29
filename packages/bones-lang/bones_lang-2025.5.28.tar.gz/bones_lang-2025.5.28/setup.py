from setuptools import setup, find_packages
from distutils.core import Extension

# read the contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


NP_VERSION = '1.17.3'
CP_VERSION = '2025.5.28'
BL_VERSION = "2025.5.28"


# print(find_packages())


setup(
    name='bones-lang',
    install_requires=[
        f'coppertop-bones >= {CP_VERSION}',
        f'numpy >= {NP_VERSION}'
    ],
    version=BL_VERSION,
    packages=[
        'bones',
        'bones.kernel',
        'bones.lang',
    ],
    # ext_modules=[Extension("bones.jones", ["./bones/c/jones/__jones.c"])],
    # package_dir = {'': 'core'},
    # namespace_packages=['coppertop_'],
    python_requires='>=3.11',
    license='License :: OSI Approved :: Apache Software License',
    description = 'Python implementation of the bones language',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author = 'David Briant',
    author_email = 'dangermouseb@forwarding.cc',
    url = 'https://github.com/coppertop-bones/bones',
    download_url = '',
    keywords = [
        'multiple', 'dispatch', 'piping', 'pipeline', 'pipe', 'functional', 'multimethods', 'multidispatch',
        'functools', 'lambda', 'curry', 'currying'
    ],
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
