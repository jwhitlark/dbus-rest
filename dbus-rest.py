#! /usr/bin/env python

"""Restful HTTP interface to DBUS, served only to the local system.

Copyright (c) 2009 Jason Whitlark <jason@whitlark.org>

Will be under the eclipse public license, as soon as I get my act together.
"""

#TODO: add nice error msgs/return codes if required libraries are missing.
import dbus
import simplejson
from urlparse import parse_qs, urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def get_dbus_interface(bus, service, path, interface, method, args):
    obj = bus.get_object(service, path)
    interface = getattr(obj, method)
    return apply(interface, args)


class DBusHandler(BaseHTTPRequestHandler):
""" Example call: http://localhost:9880/dbus/session/call/org.gnome.Tomboy.RemoteControl/ListAllNotes/?service=org.gnome.Tomboy&path=/org/gnome/Tomboy/RemoteControl

arguments are / separated after the method name (ListAllNotes in the above example)
"""
    def compose_header(self):
            self.send_response(200)
            # CLEANUP: the standards say application/json, this is mostly for testing...
            self.send_header('Content-type', 'text/html')
            self.end_headers()

    def do_GET(self):
        # path: /org/gnome/Tomboy/RemoteControl?foo=bar
        self.compose_header()
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        get_param = lambda x : params.get(x, None)[0]

        if path.startswith("/dbus"):
            path = path[5:]
            if path.startswith("/session"):
                self.bus = dbus.SessionBus()
                path = path[8:]
            elif path.startswith("/service"):
                self.bus = dbus.ServiceBus()
                path = path[8:]
            else:
                self.send_error(400, "Bad DBUS bus name: must be session or service")

            if path.startswith("/call"):
                parts = path[6:].split('/')
                interface = parts[0]
                method = parts[1]
                args = parts[2:]
                if args == ['']:  # FIXME: ugly
                    args = []
                dbus_result = get_dbus_interface(self.bus, get_param('service'), get_param('path'),
                                                 interface, method, args)
                # TODO: check DBus spec, are there types that simplejson
                # doesn't support out of the box?
                reply = simplejson.dumps(dbus_result)
            elif path.startswith("/register"):
                # This one could be complcated, caller needs to
                # provide a set of callbacks, and even introspection?
                reply = "Not Implemented."
            elif path.startswith("/subscribe"):
                # caller must supply http callback address, perhaps
                # only on localhost?
                reply = "Not Implemented."
            else:
                self.send_error(400, "Bad DBUS interaction: must be call, register, or subscribe.")
        else:
            self.send_error(400, "Path does not exist")

        self.wfile.write(reply)

def main():
    try:
        server = HTTPServer(('127.0.0.1', 9880), DBusHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl-C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

