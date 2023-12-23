#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from  cpti import NAME,SHORT_CMD
import setuptools

#readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')

install_requires=['numpy>=1.14.3']

setuptools.setup(
	name=NAME,
	setup_requires=['setuptools_scm'],
	version="0.1.6",
	author="lvxinm",
	author_email="12132772@mail.sustech.edu.cn",
	description="Inspired by DPGEN, a workflow to calculate the number\
    of electrons in a constant-potential model is established",
	python_requires="~=3.6",
	packages=['cpti',
			  'cpti/generator',
			  'cpti/dispatcher',
			  'cpti/collect',
	],
	keywords='workflow',
	install_requires=install_requires,    
		entry_points={
		'console_scripts': [
			SHORT_CMD+'= cpti.main:main']
   }
)

