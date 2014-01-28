# Superfeedr XMPP JSON API Python Wrapper

This is an updated client library for using Superfeedr's JSON XMPP subscriptions

## Requirements:

SleekXMPP
python-dateutil

## Installation:
    sudo python setup.py install

## Example

    from sfjson import Superfeedr
    import time

    def sf_message(event):
    	print "received event without entries"

    def sf_entry(event):
    	print "received entry with events", event

    sf = Superfeedr('user@superfeedr.com', 'password-here')
    sf.on_notification(sf_message)
    sf.on_entry(sf_entry)
    while True:
    	time.sleep(1)
