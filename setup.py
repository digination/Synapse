#!/usr/bin/env python

import os
import sys
import shutil


print "compiling documentation..."
os.chdir("src/doc")
os.system("./doc_compile.py >/dev/null")
os.chdir("../../")


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
shutil.copytree("./src/doc/en","/usr/share/synapse/doc")


print "copying library files"
shutil.copytree("./src/lib","/usr/lib/synapse")

print "copying main synapse scripts"
shutil.copy("./src/synapse","/usr/bin/")
shutil.copy("./src/synerpreter","/usr/bin/")


