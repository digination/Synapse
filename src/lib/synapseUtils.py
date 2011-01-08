#!/usr/bin/env python
import os
from synapseIMVEC import *
from synapseDebug import dbg
from copy import *
import time



def getAbsoluteCoords(ref,item,x,y):

   if item == ref:
      IMVEC.dbg.debug("COMPUTED ABSOLUTE COORDS: %d,%d",(x,y),dbg.EXDEBUG)
      return (x,y)
      

   ispace_coords = IMVEC.activeDoc.getCanvas().convert_from_item_space(item,item.get_property("x"),item.get_property("y"))
   
   x += ispace_coords[0]
   y += ispace_coords[1]

   if (item.get_parent() != None):

      (x,y) = getAbsoluteCoords(ref,item.get_property("parent"),x,y)    
   
   
   return (x,y)





def resclaleColorSel(color):

      if len(color) <= 7:
         return color

      hexr=""
      hexg=""
      hexb=""

      (r,g,b) = (0,0,0)

      result ="#";

      color = color.lstrip('#')
      

      for i in range(0,4):
         hexr += color[i]
      for i in range(4,8):
         hexg += color[i]
      for i in range(8,12):
         hexb += color[i]

      r = int(hexr,16)
      g = int(hexg,16)
      b = int(hexb,16)

      r = r >> 8
      g = g >> 8
      b = b >> 8


      result += "%02x%02x%02x" % (r,g,b)
      return result




def resolve(objname):

   found_results = list()

   for obj in IMVEC.activeDoc.getContainer().getSynObjects():

      if obj.getName() == objname:

         found_results.append(obj)

   if (len(found_results) == 0 ):
      return None
   elif (len(found_results) == 1 ):
      return found_results[0]
   else:
      return found_results


class CPUsage:
   def __init__(self, interval=0.1, percentage=True):
       self.interval=interval
       self.percentage=percentage
       self.result=self.compute()
      
   def get_time(self):
       stat_file=file("/proc/stat", "r")
       time_list=stat_file.readline().split(" ")[2:6]
       stat_file.close()
       for i in range(len(time_list))  :
           time_list[i]=int(time_list[i])
       return time_list
  
   def delta_time(self):
       x=self.get_time()
       time.sleep(self.interval)
       y=self.get_time()
       for i in range(len(x)):
           y[i]-=x[i]
       return y   

   def compute(self):
       t=self.delta_time()
       if self.percentage:
           result=100-(t[len(t)-1]*100.00/sum(t))
       else:
           result=sum(t)
       return result
  

   def getResult(self):
       return self.result
   #def __repr__(self):
       #return str(self.result)

