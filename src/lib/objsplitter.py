#!/usr/bin/env python
import os

## script to prepare objects cutting from source, for version 0.2

fh = open("synapseObjects.py","r")

lines = fh.readlines()


for line in lines:

    

   if line.find("class") == 0 and line.find("(synobj)") > 0: 
      class_str = "from synapseObjects import synobj\n"  
      class_name = line.rstrip("\n").replace("class ","").replace("(synobj):","")

      os.system("echo \"\" > synobjects/%s.py" % (class_name) )     
      os.system("cat header.txt >> synobjects/%s.py" % (class_name) )




      
