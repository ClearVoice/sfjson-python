#!/usr/bin/env python

""" Tests for sfjson
You must set the sf_jid and sf_token environment variables to run these tests.
"""

import os
import unittest
from sfjson import Superfeedr
from xml.etree import cElementTree as Element
from sleekxmpp import StanzaBase

import logging
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s')


class SuperfeedrJSONTest(unittest.TestCase):

    jid = None
    token = None
    sf_client = None

    @classmethod
    def setUpClass(cls):
        cls.jid = os.environ.get('sf_jid')
        cls.token = os.environ.get('sf_token')
        cls.sf_client = Superfeedr(cls.jid, cls.token)

    @classmethod
    def tearDownClass(cls):
        cls.sf_client.disconnect()

    def test_connected(self):
        assert self.sf_client.success

    def test_subscribe(self):
        assert self.sf_client.subscribe(['http://superfeedr.com/track?include=iacquire'])

    def test_unsubscribe(self):
        assert self.sf_client.unsubscribe('http://superfeedr.com/track?include=iacquire')

    def test_message_parse(self):

        xml = Element.fromstring(file('sfjson_msg.xml', 'rb').read())
        stanza = StanzaBase(xml=xml)
        result = self.sf_client.superfeedr_msg(stanza)

        assert result['status']['feed'] == 'http://superfeedr.com/track?include=apple'
        assert result['items'][0]['title'] == 'iPad Air : une grosse autonomie, mais pas la plus grosse'

if __name__ == '__main__':
    unittest.main()