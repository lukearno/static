import os

from setuptools import setup, find_packages


with open('README.md') as readme_file:
    README = readme_file.read().strip()

PROJECT = README.strip('#').split('\n')[0].strip().split()[0].lower()
DESCRIPTION = README.split('\n')[2]

with open('%s/VERSION' % PROJECT) as version_file:
    VERSION = version_file.read().strip()

with open('requirements.txt') as reqs_file:
    REQS = reqs_file.read()

with open('entrypoints.conf') as ep_file:
    ENTRYPOINTS = ep_file.read()


setup(name=PROJECT,
      version=VERSION,
      description=DESCRIPTION,
      long_description=README,
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://github.com/lukearno/%s' % PROJECT,
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=REQS,
      entry_points=ENTRYPOINTS,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])
