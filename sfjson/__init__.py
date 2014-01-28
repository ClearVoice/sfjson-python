import sleekxmpp
import Queue
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath
import xml.etree.cElementTree as ElementTree
import json


class Superfeedr(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):

        self.success = False
        self.notification_callback = None
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0199')
        self.add_event_handler("session_start", self._start)
        handler = Callback('superfeedr',
                           MatchXPath("{jabber:client}message/"
                                      "{http://jabber.org/protocol/pubsub#event}event"),
                           self._superfeedr_msg, thread=False)
        self.register_handler(handler)
        self.success = self.connect(('xmpp.superfeedr.com', 5222))
        if self.success:
            self.wait_for_start = Queue.Queue()
            self.process(threaded=True)
            start = self.wait_for_start.get(10)
            if start is None:
                self.success = False

    def _start(self, event):
        self.get_roster()
        self.send_presence()
        self.wait_for_start.put(True)

    def _superfeedr_msg(self, stanza):
        xml = stanza.xml
        event = {}
        status = xml.find('{http://jabber.org/protocol/pubsub#event}event/'
                          '{http://superfeedr.com/xmpp-pubsub-ext}status')

        http = xml.find('{http://jabber.org/protocol/pubsub#event}event/'
                        '{http://superfeedr.com/xmpp-pubsub-ext}status/'
                        '{http://superfeedr.com/xmpp-pubsub-ext}http')

        next_fetch = xml.find('{http://jabber.org/protocol/pubsub#event}event/'
                              '{http://superfeedr.com/xmpp-pubsub-ext}status/'
                              '{http://superfeedr.com/xmpp-pubsub-ext}next_fetch')

        items = xml.find('{http://jabber.org/protocol/pubsub#event}event/'
                          '{http://jabber.org/protocol/pubsub#event}items')

        entries = xml.findall('{http://jabber.org/protocol/pubsub#event}event/'
                              '{http://jabber.org/protocol/pubsub#event}items/'
                              '{http://jabber.org/protocol/pubsub#event}item/'
                              '{http://jabber.org/protocol/pubsub#event}item/content')

        print "hello there"

        if None not in (status, http, next_fetch, items, entries):
            event['feed'] = items.get('node')
            event['http'] = (http.get('code'), http.text)
            event['next_fetch'] = next_fetch.text
            event['entries'] = []
            for entry in entries:
                if entry.get('type') == 'application/json':
                    event['entries'].append(json.loads(entry.text))

        self.event('superfeedr', event)
        if len(event.get('entries', [])) > 0:
            self.event('superfeedr_entry', event)

        print json.dumps(event)

    def subscribe(self, feeds):
        if len(feeds) > 20:
            raise ValueError('Maximum of 20 feeds allowed per subscription message.')

        pubsub = ElementTree.Element('{http://jabber.org/protocol/pubsub}pubsub')
        pubsub.attrib['xmlns:superfeedr'] = 'http://superfeedr.com/xmpp-pubsub-ext'

        for f in feeds:
            feed = ElementTree.Element('subscribe')
            feed.attrib['node'] = f
            feed.attrib['jid'] = self.jid
            feed.attrib['superfeedr:format'] = 'json'
            pubsub.append(feed)

        iq = self.make_iq_set(pubsub)
        iq.attrib['to'] = 'firehoser.superfeedr.com'
        iq.attrib['from'] = self.jid
        iq.attrib['type'] = 'set'
        iq_id = iq.get('id')
        result = self.send(iq, "<iq id='%s'/>" % iq_id)

        return result

    def unsubscribe(self, feed):
        return self.plugin['xep_0060'].unsubscribe('firehoser.superfeedr.com', feed)

    def list(self, page=0):
        pubsub = ElementTree.Element('{http://jabber.org/protocol/pubsub}pubsub')
        pubsub.attrib['xmlns:superfeedr'] = 'http://superfeedr.com/xmpp-pubsub-ext'
        subscriptions = ElementTree.Element('subscriptions')
        subscriptions.attrib['jid'] = self.fulljid
        subscriptions.attrib['superfeedr:page'] = str(page)
        pubsub.append(subscriptions)
        iq = self.make_iq_set(pubsub)
        iq.attrib['to'] = 'firehoser.superfeedr.com'
        iq.attrib['from'] = self.fulljid
        iq.attrib['type'] = 'get'
        iq_id = iq.get('id')
        result = self.send(iq, "<iq id='%s'/>" % iq_id)
        if result is False or result is None or result.get('type') == 'error': return False
        nodes = result.findall(
            '{http://jabber.org/protocol/pubsub}pubsub/{http://jabber.org/protocol/pubsub}subscriptions/{http://jabber.org/protocol/pubsub}subscription')
        if nodes is None:
            return []
        nodelist = []
        for node in nodes:
            nodelist.append(node.get('node', ''))
        return nodelist

    def on_notification(self, callback):
        self.add_event_handler('superfeedr', callback)

    def on_entry(self, callback):
        self.add_event_handler('superfeedr_entry', callback)
