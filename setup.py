from setuptools import setup, find_packages
import sys
import os

version = '0.0'

setup(name='jslcrud',
      version=version,
      description="JSON Schema CRUD for Morepath",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='morepath jsonschema crud',
      author='Izhar Firdaus',
      author_email='izhar@abyres.net',
      url='http://github.com/abyres',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'morepath',
          'jsl',
          'more.jsonschema',
          'sqlalchemy',
          'sqlalchemy_jsonfield',
          'more.signals',
          'more.basicauth',
          'DateTime',
          'transitions',
          'jsonpath_ng',
          'python-dateutil',
          'more.jwtauth',
          'sqlsoup',
          'celery',
          'gunicorn',
          'itsdangerous',
          'pyyaml',
          'passlib',
          'jsonschema',
          'more.transaction',
          'zope.sqlalchemy',
          'python-dateutil',
          'more.cors'
      ],
      extras_require={
          'test': [
              'nose',
              'webtest',
              'pytest'
          ]
      },
      entry_points={
          'morepath': [
              'scan = jslcrud'
          ]
      }
      )
