from setuptools import setup, find_packages
from distutils.core import Extension

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = "2025.05.01.1"

# print(find_packages())

setup(
  name='coppertop-bones',
  url = 'https://github.com/coppertop-bones/coppertop',

  packages=[
    'bones',
    'bones.core',
    'bones.kernel',
    'bones.lang',
    'bones.ts',
    'bones.ts._type_lang',
    'coppertop',
  ],

  install_requires=[
    'coppertop-bones-kernel',
    'numpy >= 1.17.3'
  ],
  python_requires='>=3.11',

  # ext_modules=[Extension("bones.jones", ["./bones/c/jones/__jones.c"])],
  # package_dir = {'': 'core'},
  # namespace_packages=['coppertop_'],
  version=VERSION,
  license='OSI Approved :: Apache Software License',
  description = 'Multiple-dispatch, partial functions and pipeline operator for Python',
  long_description_content_type='text/markdown',
  long_description=long_description,
  author = 'David Briant',
  author_email = 'dangermouseb@forwarding.cc',
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

