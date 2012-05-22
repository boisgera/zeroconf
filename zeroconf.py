#!/usr/bin/env python
# coding: utf-8

"""
Simple/Pythonic Zeroconf Service Search/Registration
"""

__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__ = "https://github.com/boisgera/zeroconf" 
__version__ = "0.0.0"

# Python 2.7 Standard Library
import pipes
import re
import subprocess
import sys
import time

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

if sys.platform.startswith("linux"):
    # Third-Party Libraries
    import pbs as host
    
    if not host.which("avahi-browse"):
        raise ImportError("unable to find avahi command-line tools")
elif sys.platform.startswith("win"):        
    try:
        process = subprocess.Popen("dns-sd", startupinfo=startupinfo)
        process.kill()
    except WindowsError:
        raise ImportError("unable to find dns-sd command-line tools")
        
# Service Search
# ------------------------------------------------------------------------------
def search(name=None, type=None, domain="local"):
    """
    Search available zeroconf services

    The result is a dictionary with service (name, type, domain) keys 
    and data values ; data are dictionaries with "hostname", "address", 
    "port" and "txt" keys.
    """
    def name_match(service):
        name_, _, _ = service
        return (name is None or name_ == name)
            
    if sys.platform.startswith("linux"):
        
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
                symbol, _, ip_version, name_, type_, domain_, \
                hostname, address, port, txt = result
                name_ = decode(name_)
                if ip_version == "IPv4":
                    info[(name_, type_, domain_)] = {"hostname": hostname,
                                                     "address" : address ,
                                                     "port"    : port    ,
                                                     "txt"     : txt     }
    
        filtered_info = [item for item in info.items() if name_match(item[0])]
        return dict(filtered_info)
        
    elif sys.platform.startswith("win"):  

        if not type:
            type = "."
            
        process = subprocess.Popen("dns-sd -Z " + type + " " + domain, \
                                   stdout=subprocess.PIPE, \
                                   startupinfo=startupinfo) 
        time.sleep(0.1)
        process.kill()
        results = process.stdout.read()
        results =  [line.split() for line in results.splitlines()]
    
        info = {}
        name_ = port = hostname = address = ""
        
        for result in results:
            
            if len(result) == 14 and result[1] == "SRV":
                name_ = decode(result[0]).split(".")[0]
                port = result[4]
                hostname = result[5]
                address = get_address(hostname)
                
            if len(result) == 3 and result[1] == "TXT":
                txt = str.replace(result[2],'"','')
                info[(name_, type, domain)] = {"hostname": hostname,
                                                 "address" : address ,
                                                 "port"    : port    ,
                                                 "txt"     : txt      }
    

        filtered_info = [item for item in info.items() if name_match(item[0])]
        return dict(filtered_info)

def get_address(hostname):
    process = subprocess.Popen("dns-sd -Q " + hostname, 
                         stdout=subprocess.PIPE, startupinfo=startupinfo) 
    time.sleep(0.1)
    process.kill()
    results = process.stdout.read()
    results =  [line.split() for line in results.splitlines()]
    
    if len(results) >= 1:
        return results[1][len(results[1]) - 1]                
    return ''

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

# Service Registration
# ------------------------------------------------------------------------------
_publishers = {} # service publisher processes identified by (name, type, port)

def register(name, type, port):
    port = str(port)
    if (name, type, port) in _publishers:
        raise RuntimeError("service already registered")
    else:
        args = ["avahi-publish", "-s", name, type, port]
        publisher = subprocess.Popen(args, stderr=subprocess.PIPE, \
                                           stdout=subprocess.PIPE)
        _publishers[(name, type, port)] = publisher

def unregister(name=None, type=None, port=None):
    if port:
        port = str(port)
    pids = []
    for name_, type_, port_ in _publishers:
        if (name is None or name_ == name) and \
           (type is None or type_ == type) and \
           (port is None or port_ == port):
           pids.append((name_, type_, port_))
    for pid in pids:
        _publishers[pid].kill()
        del _publishers[pid]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
