import threading
import signal
import os
import sys
from synapseDebug import *
import time

class thwrapper(threading.Thread):


   def setMethod(self,method):
      self.method = method   

   def run(self):
      self.method()


class synapseEngine:


   def __init__(self,debugger):

      self.dbg = debugger
      self.woiWatchAlive = False
      self.running = False  

   def woiWatchThread(self):

      while(self.woiWatchAlive):

         for obj in self.woiObjects:

            if obj.getIbuff() != "" and not obj.isRunning() :

               th0 = thwrapper()
               th0.setMethod(obj.run)
               th0.start()
              
               self.dbg.debug("THREAD FOR ITEM %s STARTED",(obj),dbg.NOTICE)
               
               
         time.sleep(0.001)



   def playWorkflow(self,objlist):
  
      self.woiObjects = list()

      if (self.running == False):
      #define a boolean executable attr for synObjects to avoid repeted and ...

         for obj in objlist:
            if (str(obj.__class__) == "dummy"):
               obj.run()
               self.dbg.debug("THREAD FOR ITEM %s STARTED",(obj),dbg.NOTICE)

            elif (str(obj.__class__) != "synapseObjects.syncom") \
            and (str(obj.__class__) != "synapseObjects.synlink") \
            and (str(obj.__class__) != "synapseObjects.syncontainer") \
            and (obj.getWOI() == False):
               th0 = thwrapper()
               th0.setMethod(obj.run)
               th0.start()
               self.dbg.debug("THREAD FOR ITEM %s STARTED",(obj),dbg.NOTICE)
            elif (str(obj.__class__) != "synapseObjects.syncom") \
            and (str(obj.__class__) != "synapseObjects.synlink") \
            and (str(obj.__class__) != "synapseObjects.syncontainer") \
            and (obj.getWOI() == True):
               self.woiObjects.append(obj)

         if len(self.woiObjects) != 0:
            th1 = thwrapper()
            th1.setMethod(self.woiWatchThread)
            self.woiWatchAlive = True
            th1.start()
            self.dbg.debug("THREAD WOI WATCHER STARTED",tuple(),dbg.NOTICE)
        
         self.running = True    


   def stopWorkflow(self,objlist):

         try:
            if self.woiWatchAlive:
               self.dbg.debug("WOI WATCH THREAD STOPPED",tuple(),dbg.NOTICE)
               self.woiWatchAlive = False
         except:
            pass


         for obj in objlist:
            if (str(obj.__class__) != "synapseObjects.syncom") \
            and (str(obj.__class__) != "synapseObjects.synlink") \
            and (str(obj.__class__) != "synapseObjects.syncontainer"):
               if (obj.isRunning()):
                  self.dbg.debug("THREAD FOR ITEM %s STOPPED",(obj),dbg.NOTICE)
                  obj.kill()
               if (str(obj.__class__) == "synapseObjects.synmonitor"):
                  #IMVEC.activeDoc.getContainer().getMemberFromSynObj(obj).getSynItem().flush()
                  obj.flush()
         self.running = False
