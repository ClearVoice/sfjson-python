#!/usr/bin/env python

import os
import unittest
from sfjson import Superfeedr

import logging
logging.basicConfig(level=logging.DEBUG)

# very early tests


class SuperfeedrJSONTest(unittest.TestCase):

    def setUp(self):
        self.jid = os.environ.get('sf_jid')
        self.token = os.environ.get('sf_token')

    # def test_connect(self):
    #
    #     sf_client = Superfeedr(self.jid, self.token)
    #
    #     assert sf_client.success
    #
    #     sf_client.disconnect()

    def test_subscribe(self):

        sf_client = Superfeedr(self.jid, self.token)

        sf_client.subscribe(['http://superfeedr.com/dummy.xml'])

        assert True
