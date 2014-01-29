#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '1.0.0'
DESCRIPTION = 'sfjson'
LONG_DESCRIPTION = """
sfjson is a Superfeedr JSON wrapper for SleekXMPP
SleekXMPP is an elegant Python library for XMPP (aka Jabber, Google Talk, etc).
"""

setup(
    name="sfjson",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Jeff Nappi',
    author_email='jeff [at] iacquire.com',
    url='https://github.com/iAcquire/sfjson-python',
    license='MIT',
    packages=['sfjson'],
    install_requires=['sleekxmpp', 'tlslite', 'pyasn1', 'pyasn1-modules', 'python-dateutil'],
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    )
)
