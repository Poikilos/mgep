#!/usr/bin/env python
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='mgep',
      version='0.1',
      description='Minimal Game Engine for Pygame',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: pygame',
      ],
      keywords='minimal minimalist game engine python pygame mgep',
      url='http://github.com/poikilos/mgep',
      author='Jacob Gustafson',
      author_email='7557867+poikilos@users.noreply.github.com',
      license='GPLv3+',
      packages=['mgep'],
      install_requires=[
          'pygame',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': ['mgep-cli=mgep.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)
