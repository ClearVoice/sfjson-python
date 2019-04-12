# Superfeedr XMPP JSON API Python Wrapper

This is an updated client library for using Superfeedr's JSON XMPP subscriptions

## Requirements:

At the time of release these specific dependency versions should be used:

SleekXMPP==1.2.5 (1.3.3 seems to have SSL issues)
pyasn1==0.3.7
pyasn1-modules==0.1.5
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
