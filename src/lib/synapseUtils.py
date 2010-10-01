#!/usr/bin/env python
import os
from synapseIMVEC import *
from synapseDebug import dbg
from copy import *



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

