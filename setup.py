#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Nathanael C. Fritz
# All Rights Reserved
#
# This software is licensed as described in the README file,
# which you should have received as part of this distribution.
#

from distutils.core import setup

VERSION = 'v14.01.27a'
DESCRIPTION = 'sfjson'
LONG_DESCRIPTION = """
sfjson is a Superfeedr JSON wrapper for SleekXMPP
SleekXMPP is an elegant Python library for XMPP (aka Jabber, Google Talk, etc).
"""

CLASSIFIERS = ['Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License',
               'Programming Language :: Python',
               'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name="sfjson",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Jeff Nappi',
    author_email='jeff [at] iacquire.com',
    url='https://github.com/iAcquire/sfjson-python',
    license='MIT',
    platforms=['any'],
    packages=['sfjson'],
    requires=['sleekxmpp', 'tlslite', 'pyasn1', 'pyasn1-modules']
)

