#!/usr/bin/env python


import libxml2
import time
import traceback
import sys
import logging
import os

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.all import Client

from subprocess import Popen, PIPE
from fcntl import fcntl , F_GETFL, F_SETFL
import select
import signal
import threading


class injectorThread(threading.Thread):
     
   def setConnector(self,conn0):

      self.conn0 = conn0   

   def getProc(self):

      return self.proc

   def run(self):
      
      if (self.conn0.getObj().getInjectType() == "String"):

         self.conn0.broadcast(self.conn0.getObj().getData())


      elif (self.conn0.getObj().getInjectType() == "Multiline String"):

         

              
      elif (self.conn0.getObj().getInjectType() == "Multiline String"):
      


class appThread(threading.Thread):
     
   def setConnector(self,conn0):

      self.conn0 = conn0   

   def getProc(self):

      return self.proc

   def run(self):
      self.proc = Popen(self.conn0.getApp().getCmd(), shell=True, stdout=PIPE,stdin=PIPE,bufsize=4096)
      fcntl(self.proc.stdout,F_SETFL,fcntl(self.proc.stdout,F_GETFL) | os.O_NONBLOCK)
      fcntl(self.proc.stdin,F_SETFL,fcntl(self.proc.stdin,F_GETFL) | os.O_NONBLOCK)      


      while self.proc.returncode == None:  
        
         if self.conn0.getSessStatus() == False:
            print "(THREAD) NOT CONNECTED !!"

         self.proc.poll()

         (rr,wr,er) = select.select([self.proc.stdout],[],[],1)
		    
         for fd in rr:
            line = fd.read()
            print line
            self.conn0.broadcast(line)

      self.conn0.broadcast("SYNAPP_END")




class connector(Client):

   def got_message(self, stanza):
      print stanza.get_from().node, ":", stanza.get_body() 

      proc = self.appT.getProc()
      proc.stdin.write(stanza.get_body())
      proc.stdin.flush()
     


   def getSessStatus(self):

      return self.session_established   

   def session_started(self):
      self.get_stream().set_message_handler("chat", self.got_message)
      self.stream.send(Presence())

   def setApp(self,app):
      self.app = app
 
   def getApp(self):

      return self.app
     
   def run(self):
     
      self.appT = appThread()
      self.appT.setConnector(self)
      self.appT.start()
      self.loop(1)

      
   def idle(self):
        Client.idle(self)
        
       
   def broadcast(self,message):

      if not self.session_established:
         print "ERROR: NOT CONNECTED"

      for peer in self.app.getPeers():
         print "SENDING MESSAGE TO %s" % (peer)
         target=JID(peer,self.jid.domain)
         self.get_stream().send(Message(stanza_type='chat',to_jid=target,body=unicode(message,"utf-8")))


         

