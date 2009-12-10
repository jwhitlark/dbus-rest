#! /usr/bin/env python

"""Restful HTTP interface to DBUS, served only to the local system.

Copyright 2009 Jason Whitlark

Will be under the eclipse public license, as soon as I get my act together.
"""

import dbus
import simplejson
from urlparse import parse_qs, urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

sessionBus = dbus.SessionBus()

# system or service?
def get_dbus_interface(service, path, interface, method, *args):
    obj = sessionBus.get_object(service, path)
    print service, path, interface, args
    interface = getattr(obj, method)
    return interface() #*args)

class MyHandler(BaseHTTPRequestHandler):

#can be called with something like: http://localhost:9880/?service=org.gnome.Tomboy&path=/org/gnome/Tomboy/RemoteControl&interface=org.gnome.Tomboy.RemoteControl&method=ListAllNotes&args=None

    def do_GET(self):
        # path: /org/gnome/Tomboy/RemoteControl?foo=bra
        self.send_response(200)
        self.send_header('Content-type', 'text/json')  # make this json or xml later?
        self.end_headers()
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        print params
        out = get_dbus_interface(params['service'][0], params['path'][0], params['interface'][0], params['method'][0], params['args'][0])
        self.wfile.write(simplejson.dumps(out))
        return

def main():
    try:
        server = HTTPServer(('127.0.0.1', 9880), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl-C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

