from setuptools import setup, find_packages

# read the contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


version = "2025.05.01.1"


# print(find_packages())


setup(
  name = 'coppertop-bones-dm',
  packages = [
    'dm',
    'dm._core',
    'dm.core',
    'dm.finance',
    'dm.frame',
    'dm.linalg',
    'dm.linalg.algos',
    'dm.utils',
  ],
  # package_dir = {'': 'core'},
  # namespace_packages=['coppertop_'],
  version = version,
  python_requires = '>=3.11',
  license = 'OSI Approved :: Apache Software License',
  description = 'The dangermouse standard library for coppertop and bones',
  long_description_content_type='text/markdown',
  long_description=long_description,
  author = 'David Briant',
  author_email = 'dangermouseb@forwarding.cc',
  url = 'https://github.com/coppertop-bones/dm',
  download_url = '',
  # download_url = f'https://github.com/coppertop-bones/dm/archive/{version}.tar.gz', not maintained
  keywords = ['multiple', 'dispatch', 'piping', 'pipeline', 'pipe', 'functional', 'multimethods', 'multidispatch',
            'functools', 'lambda', 'curry', 'currying', 'dataframe', 'polars', 'pandas'],
  install_requires=['coppertop-bones'],
  include_package_data=True,
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Topic :: Utilities',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.11',
  ],
  zip_safe=False,
)
