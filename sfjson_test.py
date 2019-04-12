#!/usr/bin/env python

""" Tests for sfjson
You must set the sf_jid and sf_token environment variables to run these tests.
"""

import os
import unittest
from sfjson import Superfeedr
from xml.etree import cElementTree as Element
from sleekxmpp.xmlstream import StanzaBase

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
        url = 'http://superfeedr.com/track?include=iacquire'

        result = self.sf_client.subscribe([url])

        assert result[0]['subscription']['feed']['url'] == url

    def test_list(self):
        url = 'http://superfeedr.com/track?include=iacquire'

        self.sf_client.subscribe([url])

        feeds = self.sf_client.list()

        assert 'http://superfeedr.com/track?include=iacquire' in feeds

    def test_unsubscribe(self):
        assert self.sf_client.unsubscribe('http://superfeedr.com/track?include=iacquire')
        assert self.sf_client.unsubscribe('http://www.iacquire.com/feed/')

    def test_message_parse(self):

        expected_title = 'iPad Air : une grosse autonomie, mais pas la plus grosse'

        with open('sfjson_msg.xml', 'rb') as f:
            xml = Element.fromstring(f.read())
        stanza = StanzaBase(xml=xml)
        result = self.sf_client.superfeedr_msg(stanza)

        assert result['status']['feed'] == 'http://superfeedr.com/track?include=apple'
        assert result['items'][0]['title'] == expected_title

if __name__ == '__main__':
    unittest.main()
