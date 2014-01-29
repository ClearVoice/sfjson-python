from xml.etree import cElementTree as ElementTree
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath
from sleekxmpp.xmlstream.matcher import MatcherId
from sleekxmpp.xmlstream.handler import Waiter
from sleekxmpp import ClientXMPP
from Queue import Queue
from sfjson.util import date_to_epoch
import json


class Superfeedr(ClientXMPP):
    def __init__(self, jid, password, auto_connect=True):

        ClientXMPP.__init__(self, jid, password)

        self.success = False
        self.notification_callback = None
        self.wait_for_start = Queue()

        self.register_plugin('xep_0004')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0199')
        self.add_event_handler("session_start", self.start)

        handler = Callback('superfeedr',
                           MatchXPath("{jabber:client}message/"
                                      "{http://jabber.org/protocol/pubsub#event}event"),
                           self.superfeedr_msg)

        self.register_handler(handler)

        if auto_connect:
            self.connect_wait()

    def connect_wait(self, timeout=10):
        self.success = self.connect(('xmpp.superfeedr.com', 5222))
        if self.success:
            self.process(threaded=True)
            start = self.wait_for_start.get(timeout)
            if start is None:
                self.success = False

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.wait_for_start.put(True)

    def superfeedr_msg(self, stanza):
        xml = stanza.xml

        event = {'items': [],
                 'status': self.parse_status(xml, '{http://jabber.org/protocol/pubsub#event}event')}

        items = xml.findall('{http://jabber.org/protocol/pubsub#event}event/'
                            '{http://jabber.org/protocol/pubsub#event}items/'
                            '{http://jabber.org/protocol/pubsub}item/'
                            '{http://www.w3.org/2005/Atom}content')

        for item in items:
            if item.get('type') == 'application/json':
                event['items'].append(json.loads(item.text))

        self.event('superfeedr', event)
        if len(event.get('items', [])) > 0:
            self.event('superfeedr_entry', event)

        return event

    def subscribe(self, feeds):
        if len(feeds) > 20:
            raise ValueError('Maximum of 20 feeds allowed per subscription message.')

        pubsub = ElementTree.Element('{http://jabber.org/protocol/pubsub}pubsub')
        pubsub.attrib['xmlns:superfeedr'] = 'http://superfeedr.com/xmpp-pubsub-ext'

        for f in feeds:
            feed = ElementTree.Element('subscribe')
            feed.attrib['node'] = f
            feed.attrib['jid'] = self.boundjid.bare
            feed.attrib['superfeedr:format'] = 'json'
            pubsub.append(feed)

        iq = self.make_iq_set(pubsub)
        iq.attrib['to'] = 'firehoser.superfeedr.com'
        iq.attrib['from'] = self.boundjid.bare
        iq.attrib['type'] = 'set'

        response = self.send_wait(iq)

        subscriptions = response.findall('{http://jabber.org/protocol/pubsub}pubsub/'
                                         '{http://jabber.org/protocol/pubsub}subscription')
        result = False
        if subscriptions:
            result = []
            for subscription in subscriptions:
                status = self.parse_status(subscription)
                result.append({"subscription": {"status": status,
                                                "feed": {"url": subscription.get('node'),
                                                         "title": status['title']}}})
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

        result = self.send_wait(iq)

        if not result or result.get('type') == 'error':
            return False

        nodes = result.findall('{http://jabber.org/protocol/pubsub}pubsub/'
                               '{http://jabber.org/protocol/pubsub}subscriptions/'
                               '{http://jabber.org/protocol/pubsub}subscription')
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

    def send_wait(self, iq, timeout=None):
        """
         :param iq: Stanza to send
         :param int timeout: The number of seconds to wait for the stanza
            to arrive. Defaults to the the stream's
            :class:`~sleekxmpp.xmlstream.xmlstream.XMLStream.response_timeout`
            value.
        """

        iq_id = iq.get('id')
        self.send(iq)

        waiter = Waiter("SendWait_%s" % self.new_id(), MatcherId(iq_id))
        self.register_handler(waiter)

        return waiter.wait(timeout)

    @staticmethod
    def parse_status(xml, base_query=None):

        base_query = base_query + '/' if base_query else ''
        status_query = base_query + '{http://superfeedr.com/xmpp-pubsub-ext}status'
        status_child_query = status_query + '/{http://superfeedr.com/xmpp-pubsub-ext}'

        status = xml.find(status_query)
        http = xml.find(status_child_query + 'http')
        next_fetch = xml.find(status_child_query + 'next_fetch')
        last_fetch = xml.find(status_child_query + 'last_fetch')
        last_parse = xml.find(status_child_query + 'last_parse')
        period = xml.find(status_child_query + 'period')
        last_maintenance_at = xml.find(status_child_query + 'last_maintenance_at')
        title = xml.find(status_child_query + 'title')

        if None not in (status, http, next_fetch, last_fetch, last_parse, period,
                        last_maintenance_at, last_fetch, title):

            result = dict(lastParse=date_to_epoch(last_parse.text),
                          lastFetch=date_to_epoch(last_fetch.text),
                          nextFetch=date_to_epoch(next_fetch.text),
                          lastMaintenanceAt=date_to_epoch(last_maintenance_at.text),
                          period=period.text,
                          title=title.text)

            feed = status.get('feed')
            if feed is not None:
                result['feed'] = feed

            if http.text is not None:
                result['http'] = http.text

            code = http.get('code')
            if code:
                result['code'] = http.get('code')

        return result


