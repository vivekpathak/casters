#!/usr/bin/env python

from distutils.core import setup

setup(name='casters',
      version='1.0',
      description='Couchdb view/code maintenance utilities',
      author='Vivek Pathak',
      #author_email='tbd',
      #url='https://github.com/vivekpathak/casters',
      packages=['casters'],
      data_files=[('resources', ['caster_harness.js',
                                 'map.js',
                                 'testExample.js',
                                 'libSlowFiboExample.js',
                                 'reduce.js',
                                 'validate_doc_update.js'])]
     )
