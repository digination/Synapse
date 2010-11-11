import os
import sys
import datetime

class dbg:

   CRITICAL = 0x01
   ERROR = 0x02
   WARNING = 0x03
   NOTICE = 0x04
   DEBUG = 0x05
   EXDEBUG = 0x06
   SEXDEBUG = 0x07


   prefixes = {

   0x01: "[CRITICAL]\t",
   0x02: "[ERROR]\t",
   0x03: "[WARNING]\t",
   0x04: "[NOTICE]\t",
   0x05: "[DEBUG]\t",
   0x06: "[EXDEBUG]\t",
   0x07: "[SEXDEBUg]\t"
  

   }

   def debug(self,msg_template,arg_tuple,level):

      if (level <= self.debug_level):

         if (level == dbg.CRITICAL):

           print >> sys.stderr, str(datetime.datetime.now()) , dbg.prefixes[level] ,msg_template % arg_tuple

         else:
           
           print str(datetime.datetime.now()) , dbg.prefixes[level] ,msg_template % arg_tuple      


   def __init__(self,debug_level):

      self.debug_level = debug_level


   

   
