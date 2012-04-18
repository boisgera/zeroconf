#!/usr/bin/env python
# coding: utf-8

"""
Simple/Pythonic Zeroconf Publish/Discover
"""

__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__version__ = None

# Python 2.7 Standard Library
import re
import sys

# Third-Party Libraries
import pbs as host

if sys.platform.startswith("linux"):
    if not host.which("avahi-browse"):
        raise ImportError("unable to find avahi command-line tools")

def find(name=None, type=None, domain="local"):
    """
    Find available zeroconf services

    The result is a dictionary with service (name, type, domain) keys 
    and data values ; data are dictionaries with "hostname", "address", 
    "port" and "txt" keys.
    """

    options = {"terminate"   : True  , 
               "resolve"     : True  , 
               "parsable"    : True  , 
               "no-db-lookup": True  , 
               "domain"      : domain}
    if type:
         results = host.avahi_browse(type, **options)
    else:
         results = host.avahi_browse(all=True, **options)
    results = [line.split(";") for line in results.splitlines()]

    info = {}
    for result in results:
        if result[0] == "=":
            symbol, _, ip_version, _name, _type, _domain, \
            hostname, address, port, txt = result
            _name = decode(_name)
            if ip_version == "IPv4":
                info[(_name, _type, _domain)] = {"hostname": hostname,
                                                 "address" : address ,
                                                 "port"    : port    ,
                                                 "txt"     : txt     }
    def name_match(service):
        _name, _, _ = service
        return (name is None or _name == name)

    filtered_info = [item for item in info.items() if name_match(item[0])]
    return dict(filtered_info)

def decode(text):
    r"""
    Decode string with special characters escape sequences.

    We assume that the escaping scheme follows the rules used by `avahi-browse` 
    when the `--parsable` option is enabled
    (see `avahi_escape_label` function in `avahi-common/domain.c`).

    >>> decode("abc")
    'abc'
    >>> decode(r"a\.c")
    'a.c'
    >>> decode(r"a\\c")
    'a\\c'
    >>> decode(r"a\032c")
    'a c'
    >>> decode(r"a\127c")
    'a\x7fc'
    """
    def replace(match):
        numeric, other = match.groups()
        if numeric:
            return chr(int(numeric[1:]))
        else:
            return other[1:]

    return re.sub(r"(\\\d\d\d)|(\\.)", replace, text)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

