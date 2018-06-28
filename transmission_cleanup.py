#!/usr/bin/python

###
### transmission_cleanup.py
###
### A simple script to remove torrents which have been seeding too long via Transmission JSON-RPC ###
### Requires transmissionrpc - can be installed with:
### > easy_install transmissionrpc
###
### Provided as-is where-is.  Use at your own risk + please don't ask me for support :)
###
### Copyright 2016 Dan Capper <dan@hopfulthinking.com>
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###    http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
###

import transmissionrpc
from syslog import syslog
import sys

### Set these as you require ###

secondsSeedingMax = 604800 # 1 week
host = "localhost"  # Transmission host
port = 9091         # port
user = ""           # auth user
password = ""       # auth password
timeout = 30        # timeout to make the connection

### Don't edit below this line ###

syslog('Transmission Checker connecting')
try:
    tc = transmissionrpc.Client(host, port=port, user=user, password=password, timeout=timeout)
except transmissionrpc.error.TransmissionError as err:
    errstring = "Unable to connect, error was: [{0}] - Exiting".format(err)
    syslog(errstring)
    sys.exit(errstring)
except:
    errstring = "Unexpected error {0}".format(sys.exc_info()[0])
    syslog(errstring)
    raise

session = tc.get_session()
freespace = getattr(session,"download_dir_free_space")
freespaceString = "Before - Free Space in Download dir: [{0}] GB".format(freespace/1e9)
print(freespaceString)
syslog(freespaceString)

torrents = tc.get_torrents(arguments=["id", "name", "secondsSeeding"])

countString = "Total number of Torrents: {0}".format(len(torrents))
print(countString)
syslog(countString)

for torrent in torrents:
    torrentID = getattr(torrent,"id")
    secondsSeeding = getattr(torrent,"secondsSeeding")
    name = getattr(torrent,"name")
    print("Torrent id: [{0}] [{2}] Seeding for: [{1}] seconds".format(torrentID, secondsSeeding, name.encode('utf-8')))
    if secondsSeeding > secondsSeedingMax:
        removeString = "Removing torrent {1} [{0}] has been seeding for {2} > {3}".format(torrentID, name.encode('utf-8'), secondsSeeding, secondsSeedingMax)
        print(removeString)
        syslog(removeString)
        tc.remove_torrent([torrentID], delete_data=True)

session = tc.get_session()
freespace = getattr(session,"download_dir_free_space")
freespaceString = "After - Free Space in Download dir: [{0}] GB".format(freespace/1e9)
print(freespaceString)
syslog(freespaceString)
