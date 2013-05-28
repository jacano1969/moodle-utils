#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) Marcos Talau 2013
# Author Marcos Talau (talau@users.sourceforge.net)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import urllib
import urllib2
import sys
import cookielib
import hashlib
import time
import random
from types import *
try:
    from BeautifulSoup import BeautifulSoup, SoupStrainer
except:
    print 'Please, install python-beautifulsoup'
    sys.exit(-1)
import os
import openanything
from datetime import datetime

import config

import base64

PROGRAM = "moodle-exclude-all-itens.py"
VERSION = "0.1"

cj = None
opener = None

def printm(m):
    sys.stdout.write(m)
    sys.stdout.flush()

def show_warranty():
    print """
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

def build_rand_header():
    header = config.http_headers[random.randint(0, len(config.http_headers) - 1)]

    return [('User-agent', header)]

def cookie_start(url_base):
    global cj
    global opener

    cj = cookielib.CookieJar()
    if config.proxy_enable:
        proxy_handler = urllib2.ProxyHandler({config.proxy_type: config.proxy_addr})
        opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj), openanything.SmartRedirectHandler())
    else:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), openanything.SmartRedirectHandler())

    opener.open(url_base)

def delete_confirm(url):
    request = urllib2.Request(url)
    page = opener.open(request)
    contents = page.read()

    soup = BeautifulSoup(contents)

    # confirm?
    entry = soup('form', { "method" : "post" })
    soup = BeautifulSoup(str(entry))
    names = []
    values = []
    for i in soup.findAll("input"):
        if i.get("type") == "hidden":
            names.append(i.get("name"))
            values.append(i.get("value"))
    form = dict(zip(names, values))

    url = config.url_mod
    encodedForm = urllib.urlencode(form)
    request = urllib2.Request(url, encodedForm)
    page = opener.open(request)
    contents = page.read()

    soup = BeautifulSoup(contents)

def delete_itens_from_disc(url_disc):
    url = url_disc

    printm("Openning url from disc ...")
    request = urllib2.Request(url)
    page = opener.open(request)
    contents = page.read()

    soup = BeautifulSoup(contents)

    entry = soup('div', { "class" : "singlebutton" })
    soup = BeautifulSoup(str(entry))

    names = []
    values = []
    for i in soup.findAll("input"):
        if i.get("type") == "hidden":
            names.append(i.get("name"))
            values.append(i.get("value"))
    form = dict(zip(names, values))
    printm(" OK\n")

    url = config.url_view
    printm("Running enable edit command ...")

    encodedForm = urllib.urlencode(form)
    request = urllib2.Request(url, encodedForm)
    page = opener.open(request)
    contents = page.read()

    soup = BeautifulSoup(contents)
    printm(" OK\n")

    entry = soup('a', { "class" : "editing_delete" })
    soup = BeautifulSoup(str(entry))
    printm("Found %d itens to delete.\n" % len(soup.findAll("a")))
    n = 1
    for i in soup.findAll("a"):
        printm("Deleting item #%d ..." % n)
        url_delete = config.url_base + "/course/%s" % (i.get("href"))
        delete_confirm(url_delete)
        printm(" done\n")
        n = n + 1

# do the login and start the cookies
def auth(login, password):
    global opener

    url = config.url_login

    printm("Logging ...")

    cookie_start(url)

    opener_headers = config.opener_headers

    try:
        if config.http_headers_rand:
            opener_headers = build_rand_header()
    except:
        opener.addheaders = opener_headers

    opener.addheaders = opener_headers

    form = { 
             "username" : login,
             "password" : password}

    encodedForm = urllib.urlencode(form)
    request = urllib2.Request(url, encodedForm)
    page = opener.open(request)
    contents = page.read()

    soup = BeautifulSoup(contents)
    if str(soup).find('loginerrors') != -1:
        print 'Auth fail for user %s and password %s' % (login, password)
        sys.exit(-1)

    printm(" OK\n")

def use():
    print "%s %s" % (PROGRAM, VERSION)
    print ""
    print "%s <user> <password> <full-disc-url>" % (sys.argv[0])
    print " i.e. %s user pass \"http://moodle.pg.utfpr.edu.br/course/view.php?id=73\"" % (sys.argv[0])
    sys.exit(-1)

# MAIN
if (len(sys.argv) != 4):
    use()

login = sys.argv[1]
password = sys.argv[2]
url_disc = sys.argv[3]

show_warranty()
auth(login, password)
delete_itens_from_disc(url_disc)
