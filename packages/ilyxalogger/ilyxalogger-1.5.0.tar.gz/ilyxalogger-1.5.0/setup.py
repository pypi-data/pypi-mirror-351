from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='ilyxalogger',
  version='1.5.0',
  author='ILYXAAA',
  author_email='ilyagolybnichev@gmail.com',
  description='This is the simplest module for quick console log output.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/ILYXAAA/logger',
  packages=find_packages(),
  install_requires=[],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='logging console output colorize log ',
  project_urls={
    'GitHub': 'https://github.com/ILYXAAA/'
  },
  python_requires='>=3.6'
)