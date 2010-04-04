#!/usr/bin/env python

import os
import sys
import shutil

if os.path.exists("/usr/share/synapse"):
   shutil.rmtree("/usr/share/synapse")

if os.path.exists("/usr/lib/synapse"):
   shutil.rmtree("/usr/lib/synapse")


print "creating share directory"
os.mkdir("/usr/share/synapse")


print "copying common files"
shutil.copytree("./src/icons","/usr/share/synapse/icons")
shutil.copytree("./src/images","/usr/share/synapse/images")
shutil.copytree("./src/ui","/usr/share/synapse/ui")

print "copying library files"
shutil.copytree("./src/lib","/usr/lib/synapse")

print "copying main synapse script"
shutil.copy("./src/synapse","/usr/bin/")

