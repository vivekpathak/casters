#!/usr/bin/env python

from distutils.core import setup

setup(name='casters',
      version='1.0',
      description='Couchdb view/code maintenance utilities',
      author='Vivek Pathak',
      #author_email='tbd',
      #url='https://github.com/vivekpathak/casters',
      packages=['casters'],
      data_files=[('casters/resources', ['casters/resources/caster_harness.js',
                                         'casters/resources/map.js',
                                         'casters/resources/testExample.js',
                                         'casters/resources/libSlowFiboExample.js',
                                         'casters/resources/reduce.js',
                                         'casters/resources/validate_doc_update.js'])]
     )
