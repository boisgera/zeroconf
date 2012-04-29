Zeroconf
================================================================================

A simple Python 2.7 interface to Zeroconf service discovery and Registration.

Installation
--------------------------------------------------------------------------------

The `zeroconf` module assumes that the [avahi](http://avahi.org/) command-line 
tools `avahi-browse` and `avahi-publish` are available.
On Ubuntu for example, they may me installed with:

    $ sudo apt-get install avahi-tools

The module also depend on [Andrew Moffat's subprocess wrapper][pbs]. Install
it with

    $ sudo pip install pbs

[pbs]: https://github.com/amoffat

