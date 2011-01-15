#!/usr/bin/env python

import gtk
#import glib
import goocanvas

import sys
sys.path.append("/usr/lib/synapse")
from synapseIMVEC import *
from synapseGTKProperties import *
from synapseUtils import *
from synapseDebug import dbg

from subprocess import Popen, PIPE
from fcntl import fcntl , F_GETFL, F_SETFL
import select
import signal
import os
import time
import datetime
import hashlib
import random

import copy
import socket
import pexpect
from time import strftime


try:
   import xmpp
   IMVEC.HAS_XMPP = 1
except:
   print "[WARNING] xmpp LIBRARY NOT LOADED: SYNXMPP BB WILL BE DISABLED"

try:
   from scapy import *
   IMVEC.HAS_SCAPY = 1
except:
   print "[WARNING] scapy LIBRARY NOT LOADED: SYNSCAPY BB WILL BE DISABLED"

try:
   from reportlab.pdfgen import canvas
   from reportlab.lib.units import inch
   from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
   from reportlab.lib.styles import getSampleStyleSheet
except:

   #using print here, because debug object not created yet
   print "[WARNING] REPORT API NOT LOADED: REPORT BB WILL BE UNAVAILABLE"

try:
   import MySQLdb
except:
   print "[WARNING] MYSQL LIBRARY NOT LOADED: FUNCTION WILL BE DISABLED IN SYNDB"
try:
   import psycopg2
except:
   print "[WARNING] PSQL LIBRARY NOT LOADED: FUNCTION WILL BE DISABLED IN SYNDB"


#class to embbed and manipulate synlinker objects
class container:

   def __init__(self):
      self.members = dict()

   def append(self,member):

      self.members[member.getSynObj().getId()] = member


   def getMember(self,mid):

      return self.members[mid]

   def findName(self,name):

      for mid,member in self.members.items():

         if member.getSynObj().getName() == name:
            return True
      return False

   def delete(self,dmember):

      IMVEC.dbg.debug("DELETE METHOD CALLED WITH OBJ %s",(dmember),dbg.EXDEBUG)

      for mid,member in self.members.items():

         if member == dmember:
               IMVEC.dbg.debug("DELETING MEMBER %s",(member),dbg.DEBUG)
               id_to_delete = member.getSynObj().getId()
               member.getSynObj().delete()
               del self.members[id_to_delete]
               
                
   def getMemberFromSynItem(self,synItem):
      for  mid,member in self.members.items():
         if (member.getSynItem() == synItem):
            return member
            break


   def getMemberFromSynObj(self,synObj):
      for  mid,member in self.members.items():
         if (member.getSynObj() == synObj):
            return member
            break



   def getMemberFromParentSynItem(self,parent):

      for  mid,member in self.members.items():
         if (member.getSynItem().getO() == parent):
            return member
            break


   def getMembers(self):

      return self.members


   def updatePeers(self):
      for obj in self.getSynObjects():

         obj.updatePeers() 

      for obj in self.getSynObjects():
         if str(obj.__class__) == "synapseObjects.synlink" and obj.getBidir():
            obj.setDirection()
         


   def getSynObjects(self):

      objList = list()
      for  mid,member in self.members.items():
         objList.append(member.getSynObj())
      return objList

   def getSynItems(self):

      itemList = list()
      for mid,member in self.members.items():
         itemList.append(member.getSynItem())
      return itemList


   def getSynItem(self,synObj):

      for mid,member in self.members.items():
         if (member.getSynObj() == synObj):
            return member.getSynItem()
            break

   def getSynObj(self,synItem):     
      for mid,member in self.members.items():

         if (member.getSynItem() == synItem):
            return member.getSynObj()
            break


# class that makes the link between synapse objects and synapse canvas items
class linker(object):


   def __init__(self,synObject,synItem):

      self.synObject = synObject
      self.synItem = synItem
      self.runvars = dict()


   def getRunVars(self):

      return self.runvars

   def setRunVars(self,runvars):

      self.runvars = runvars


   def setSynObj(self,synObject):

      self.synObject = synObject

   def setSynItem(self,synItem):

      self.synItem = synItem

   def getSynObj(self):

      return self.synObject

   def getSynItem(self):

      return self.synItem



   def updateCanvas(self,refresh=False):


      if refresh:
         if (self.synObject.getColor() != "DEFAULT"):

            self.synItem.getMF().set_property("fill_color",self.synObject.getColor())
            self.synItem.getLtext().set_property("fill_color",self.synObject.getColor())

         self.synItem.setText(self.synObject.getName())
         return


      newcprops = self.synObject.getCanvasProperties()
  
      self.synItem.getO().set_property("x",newcprops[0])
      self.synItem.getO().set_property("y",newcprops[1])
      self.synItem.getO().set_property("width",newcprops[2])
      self.synItem.getO().set_property("height",newcprops[3])
      self.synItem.getMF().set_property("width",newcprops[4])
      self.synItem.getMF().set_property("height",newcprops[5])

      
      



   def updateSynObjCanvasProperties(self,clipboard=False):

      canvasProperties = tuple()

      if (str(self.synItem.getO().__class__) != "goocanvas.Path" ):
         x = self.synItem.getO().get_property("x")
         y = self.synItem.getO().get_property("y")      
         width = self.synItem.getO().get_property("width")
         height = self.synItem.getO().get_property("height")
         mfwidth = self.synItem.getMF().get_property("width")
         mfheight = self.synItem.getMF().get_property("height")


         if (clipboard):
     
            canvasProperties = (x,y,width,height,mfwidth,mfheight)
            self.synObject.setCanvasProperties(canvasProperties)
            return 
           
         else:

            if self.synItem.getO().get_property("parent") == IMVEC.activeDoc.getRootItem():
               rootItem = "___root___"
            else:

               ri = self.synItem.getO().get_property("parent")             
               rootItem = IMVEC.activeDoc.getContainer().getMemberFromParentSynItem(ri).getSynObj().getId()
               IMVEC.dbg.debug("UPDATING OBJ %s ROOT CANVAS PROPERTY WITH OBJ ID %s",(self.synObject.getName(),rootItem),dbg.EXDEBUG)

            canvasProperties = (x,y,width,height,mfwidth,mfheight,rootItem)





      else:
         data = self.synItem.getO().get_property("data")
         canvasProperties = (data)

      self.synObject.setCanvasProperties(canvasProperties)



class synobj:

   nbinst = 0

   def changeAttr(self,attrname,value):

      IMVEC.dbg.debug("CHANGING ATTR %s on OBJ %s with value %s",(attrname,self,value),dbg.DEBUG)

      #try
      exec "self.%s=%s" % (attrname,value)
      gtk.gdk.threads_enter() 
      IMVEC.activeDoc.getContainer().getMembers()[self.id].updateCanvas(True) 
      gtk.gdk.threads_leave()

      #except:
         #IMVEC.dbg.debug("INVALID ATTRIBUTE CHANGE ON OBJ %s",(self),dbg.WARNING)



   def genId(self):

      rand = random.randint(1,100000000)
      date_str = str(datetime.datetime.now())
      hash_id = hashlib.sha1()
      hash_id.update("%s %d" % (date_str, rand) )

      self.id = hash_id.hexdigest()

      
   def getId(self):

      return self.id
      

   def setId(self,nid):

      self.id = nid



   def delete(self):

      del self

   def isRunning(self):

      return self.alive

   def kill(self):
      self.alive = False

   def start(self):

      self.alive = True

   def getIbuff(self):
      return self.ibuff

   def getObuff(self):
      return self.obuff

   def setObuff(self,obuff):
      self.obuff = obuff

   def appendObuff(self,buff):
      self.obuff = self.obuff + buff

   def setIbuff(self,ibuff):

      self.ibuff = ibuff
      
   def appendIbuff(self,buff):

      self.ibuff = self.ibuff + buff 
 
   def init_common(self):

      self.genId()

      self.color = "DEFAULT"
      self.mInput = False
      self.needSender = False
      self.alive = False
      self.loop_mode = False
       
  

   def broadcast(self):


      if (self.obuff.find("SYNAPSE_CHANGE_ATTR:") == 0 ):

         for peer in self.peers:

            (input_num, peerobj) = tuple(peer)

            (s0,s1,s2) = self.obuff.partition(':')
            (s3,s4,s5) = s2.partition(':')
            peerobj.changeAttr(s3,s5)
         
         return


      for peer in self.peers:

         (input_num, peerobj) = tuple(peer)         


         if (peerobj.mInput == True):

            IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
            peerobj.getIbuffs()[input_num].append("%d:%s" % (input_num,self.obuff) )
            
   
         else:

            if (peerobj.needSender == False):

               IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
               peerobj.getIbuff().append("%d:%s" % (input_num,self.obuff) )

            else:

               IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
               peerobj.getIbuff().append("%s:%d:%s" % (self.getName(),input_num,self.obuff) )
       
  
      #self.ibuff = None


   #method to override for each building block
   def init_run(self):
      return

   #method to override for each building block
   def run(self):
      return 

   def __init__(self,name):
      
      self.name = name
      synobj.nbinst+=1
      return self 
  
   def getName(self):

      return self.name   

   def setName(self,name):

      self.name = name


   def getLoopMode(self):

      return self.loop_mode


   def setLoopMode(self,loop_mode):

      self.loop_mode = loop_mode

      if (self.loop_mode):
     
         self.peers.append([0,self])

      else:

         for i in range(0,len(self.peers)):
            if self.peers[i][1] == self:
               del self.peers[i]
            
               


   def setPeers(self,peersList):

      self.peersList = peersList
   
   def getPeers(self):

      return self.peers

   def getColor(self):
      return self.color

   def setColor(self,color):
      self.color = color

   def getWOI(self):

      return self.WOI

   def setWOI(self,WOI):
      self.WOI = WOI


   ## functions for canvas data keeping for pickle/unpickle
   def getCanvasProperties(self):

      return self.canvasProperties

   def setCanvasProperties(self,canvasProperties):

      self.canvasProperties = canvasProperties


   def updatePeers(self):
      try:
         del self.peers[:]
      except:
         return 0
 
      if (self.loop_mode):
         self.peers.append([0,self]) 

      for obj in IMVEC.activeDoc.getContainer().getSynObjects():
         
         if str(obj.__class__) == "synapseObjects.synlink":
            if obj.getOutObj() == self and obj.getOutputNum() == 0:

               IMVEC.dbg.debug("UPDATING LINK FOR %s",(self),dbg.NOTICE)
               self.peers.append([obj.getInputNum(),obj.getInObj()])
               



class synheader(synobj):


   def getDate(self):

      return self.date

   def getAuthor(self):
      return self.author

   def getTitle(self):
      return self.title

   def getDescr(self):
      return self.descr


   def __init__(self,title="Workflow title",author="",date="",descr="your description here"):

      self.init_common()

      self.title = title
      self.author = author
      self.date = date
      self.descr = descr
      
      
   
    
   def onITextBufferChanged(self,textbuff):
      self.descr = textbuff.get_text(textbuff.get_start_iter(),textbuff.get_end_iter())
      IMVEC.activeDoc.getHeader().getSynItem().setWorkflowDescr(self.descr)

   def on_widget_changed(self,widget):

      if (widget == synheaderGTK.iauthor):
         self.author = widget.get_text() 
         IMVEC.activeDoc.getHeader().getSynItem().setWorkflowAuthor(widget.get_text())
      elif (widget == synheaderGTK.ititle):
         self.title = widget.get_text()
         IMVEC.activeDoc.getHeader().getSynItem().setWorkflowTitle(widget.get_text())
    
   def disconnectAll(self):
   
      synheaderGTK.iauthor.disconnect(synheaderGTK.chdict['iauthor'])
      synheaderGTK.ititle.disconnect(synheaderGTK.chdict['ititle'])
      synheaderGTK.idate.disconnect(synheaderGTK.chdict['idate']) 
      synheaderGTK.idescrBuffer.disconnect(synheaderGTK.chdict['idescrBuff'])  


   def getPropWidget(self):
  
      synheaderGTK.iauthor.set_text(self.author)
      synheaderGTK.ititle.set_text(self.title)
      synheaderGTK.idate.set_text(self.date)
      synheaderGTK.idescrBuffer.set_text(self.descr)
      
      synheaderGTK.chdict['iauthor'] = synheaderGTK.iauthor.connect("changed",self.on_widget_changed)
      synheaderGTK.chdict['ititle'] = synheaderGTK.ititle.connect("changed",self.on_widget_changed)
      synheaderGTK.chdict['idate'] = synheaderGTK.idate.connect("changed",self.on_widget_changed)
      synheaderGTK.chdict['idescrBuff'] = synheaderGTK.idescrBuffer.connect("changed",self.onITextBufferChanged)    


      return synheaderGTK.o


  
class syntimer(synobj):



   def init_run(self):
  
      self.alive = True
      runvars = dict()
      runvars['time_over'] = int(self.interval)
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)


   def run(self):
     
      runvars = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()

      time_over = runvars['time_over'] 
      time = IMVEC.engine.getTime()

      IMVEC.dbg.debug("TIME: %d TIME_OVER: %d",(time,time_over),dbg.SEXDEBUG)

      if (time >= time_over ):
      
         IMVEC.dbg.debug("TIME IS OUT!!",tuple(),dbg.SEXDEBUG)
         content = None

         if (len(self.ibuff) != 0):
            input_buffer = self.ibuff.pop(0)
            (input_num,sep,content) = input_buffer.partition(":")
            
            IMVEC.dbg.debug("%s IBUFF: %s",(self.name,content) ,dbg.DEBUG)

            self.obuff = content
            self.broadcast()

         runvars['time_over'] = IMVEC.engine.getTime() + int(self.interval)      

    
   def __init__(self,name,interval=1000,loop=False):

      self.init_common()

      self.name = name
      self.interval = interval
      self.WOI = False

      self.ibuff = list()
      self.obuff = ""
      self.peers= list()


   def getPeriod(self):
      return self.interval

   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
      
        self.color = resclaleColorSel(ncolor.to_string())
        syntimerGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)



        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def on_widget_changed(self,widget):

      if (widget == syntimerGTK.iname):
         self.name = widget.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)

      elif (widget == syntimerGTK.iinterval):
         self.interval = widget.get_text()


   def disconnectAll(self):

      syntimerGTK.iname.disconnect(syntimerGTK.chdict['iname'])
      syntimerGTK.icolorBtn.disconnect(syntimerGTK.chdict['icolorBtn'])
      syntimerGTK.iinterval.disconnect(syntimerGTK.chdict['iinterval'])      

   def getPropWidget(self):


      syntimerGTK.iname.set_text(self.name)
      syntimerGTK.icolor.set_text(self.color)
      syntimerGTK.iinterval.set_text(str(self.interval))

      syntimerGTK.chdict['iname'] = syntimerGTK.iname.connect("changed",self.on_widget_changed)
      syntimerGTK.chdict['icolorBtn'] = syntimerGTK.icolorBtn.connect("clicked",self.onColorChange)
      syntimerGTK.chdict['iinterval'] = syntimerGTK.iinterval.connect("changed",self.on_widget_changed)      



      
      return syntimerGTK.o



class synjector(synobj):


   def __init__(self,name,injectType="string",data="",linesPerBlock=1,loop=False,fileName=""):

      self.init_common()
      self.name = name
      self.WOI = False
      self.injectType = injectType
      self.data = data
      self.fileName = fileName    
      self.linesPerBlock = linesPerBlock
      self.loop = loop

      self.peers = list()
     

   #synjector read properties
   def getInjectType(self):
      return self.injectType

   def getLoop(self):
      return self.loop
   
   def getFileName(self):
      return self.fileName

   def getLinesPerBlock(self):
      return self.linesPerBlock

   def getData(self):
      return self.data


   #synjector write properties
   def setInjectType(self,injectType):
      self.injectType = injectType

   def setLoop(self,loop):
      self.loop = loop
   
   def setFileName(self,fileName):
      self.fileName = fileName

   def setLinesPerBlock(self,linesPerBlock):
      self.linesPerBlock = linesPerBlock

   def setData(self,data):
      self.data = data



   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synjectorGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def onTextChange(self,widget):
      if widget == synjectorGTK.iname:
         self.name = synjectorGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(synjectorGTK.iname.get_text())

   def disconnectAll(self):
      synjectorGTK.iname.disconnect(synjectorGTK.chdict['iname'])
      synjectorGTK.icolorBtn.disconnect(synjectorGTK.chdict['icolorBtn'])

   def getPropWidget(self):
      synjectorGTK.iname.set_text(self.name)
      synjectorGTK.icolor.set_text(self.color)
      synjectorGTK.chdict['iname'] = synjectorGTK.iname.connect("changed",self.onTextChange)
      synjectorGTK.chdict['icolorBtn'] = synjectorGTK.icolorBtn.connect("clicked",self.onColorChange)
      return synjectorGTK.o








class syntest(synobj):

   nbinst = 0


   def updatePeers(self):
    
      del self.opeers[:]
      
      for i in range(0,2):

         self.opeers.append(list())

      for obj in IMVEC.activeDoc.getContainer().getSynObjects():
         
         if str(obj.__class__) == "synapseObjects.synlink" and obj.getOutObj() == self:
            
            self.opeers[obj.getOutputNum()].append((obj.getInputNum(),obj.getInObj()))


   def __init__(self,name,testType="Stream contains"):

      syntest.nbinst+=1
      self.init_common()
      self.name = name
      self.WOI = False
      
      self.testType = testType
      self.operand = ""
      
      self.ret = "Stream"

      self.opeers = list()   
      self.ibuff = list()
      self.obuff = ""


      self.ret_dict = { "Stream" : 0, "Operand" : 1 }


      self.operation_dict = { 
      "Stream equals" : ("content == self.operand",0),   
      "Stream contains" : ("content.find(self.operand) >= 0",1),
      "int(Stream) >=" : ("int(content) >= int(self.operand)",2),
      "int(Stream) <=" : ("int(content) <= int(self.operand)",3),
      "int(Stream) <" : ("int(content) < int(self.operand)",4),
      "int(Stream) >" : ("int(content) > int(self.operand)",5)
      }


   def bcast(self,expr_tv):

      if expr_tv:
         peers = self.opeers[0]
      else:
         peers = self.opeers[1]

      if self.ret == "Operand": self.obuff = self.operand

      for peer in peers:
            (input_num, peerobj) = tuple(peer)         

            if (peerobj.mInput == True):
               IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
               #peerobj.setIbuff(input_num,self.obuff)
               peerobj.getIbuffs()[input_num].append("%d:%s" % (input_num,self.obuff) )
  
            else:

               if (peerobj.needSender == False):

                  IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
                  #peerobj.setIbuff(str(input_num) + ":" +self.obuff)
                  peerobj.getIbuff().append("%d:%s" % (input_num,self.obuff) )

               else:

                  IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuff,peerobj.getName(),input_num),dbg.DEBUG)
                  #peerobj.setIbuff(self.getName() + ":" + str(input_num) + ":" +self.obuff)
                  peerobj.getIbuff().append("%s:%d:%s" % (self.getName(),input_num,self.obuff) )



   def init_run(self):

      self.alive = True

   def run(self):

          if (len(self.ibuff) != 0):

            input_buffer = self.ibuff.pop(0)

            (input_num,sep,content) = input_buffer.partition(":")

            self.obuff = content

            exec "if %s :\n   self.bcast(True)\nelse:\n   self.bcast(False)" % ( self.operation_dict[self.testType][0] ) 
            

   def getTestType(self):
      return self.testType


   def on_widget_changed(self,widget):
    
      if (widget == syntestGTK.iname):
         self.name = widget.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)

      elif (widget == syntestGTK.iop):
         self.operand = widget.get_text()

      elif (widget == syntestGTK.itt):

         self.testType = syntestGTK.itt.get_active_text()

      elif (widget == syntestGTK.iret):

         self.ret = syntestGTK.iret.get_active_text()



   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        syntestGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()



   def disconnectAll(self):

      syntestGTK.iname.disconnect(syntestGTK.chdict['iname'])
      syntestGTK.icolorBtn.disconnect(syntestGTK.chdict['icolorBtn'])
      syntestGTK.iop.disconnect(syntestGTK.chdict['iop'])
      syntestGTK.itt.disconnect(syntestGTK.chdict['itt'])
      syntestGTK.iret.disconnect(syntestGTK.chdict['iret'])

   def getPropWidget(self):

      syntestGTK.iname.set_text(self.name)
      syntestGTK.icolor.set_text(self.color)
      syntestGTK.iop.set_text(self.operand)
      
      syntestGTK.itt.set_active(self.operation_dict[self.testType][1])
      syntestGTK.iret.set_active(self.ret_dict[self.ret])

      
      syntestGTK.chdict['iname'] = syntestGTK.iname.connect("changed",self.on_widget_changed)
      syntestGTK.chdict['icolorBtn'] = syntestGTK.icolorBtn.connect("clicked",self.onColorChange)
      syntestGTK.chdict['iop'] = syntestGTK.iop.connect("changed",self.on_widget_changed)
      syntestGTK.chdict['itt'] = syntestGTK.itt.connect("changed",self.on_widget_changed)
      syntestGTK.chdict['iret'] = syntestGTK.iret.connect("changed",self.on_widget_changed)

      return syntestGTK.o






class synlink(synobj):

   def __init__(self,name,outObj,inObj):

      self.init_common()
      self.name = name
      
      self.bidir = False
      self.outObj = outObj
      self.inObj =  inObj

      #user unmodifiable class attr
      self.outNum = 0
      self.inNum = 0

   def setBidir(self,bidir):
      self.bidir = bidir

   def getBidir(self):
      return self.bidir

   def setOutputNum(self,outNum):
      self.outNum = outNum

   def setInputNum(self,inNum):
      self.inNum = inNum

   def getOutputNum(self):
     return self.outNum

   def getInputNum(self):
      return self.inNum

   def getInObj(self):
      return self.inObj

   def getOutObj(self):
      return self.outObj

   def disconnectAll(self):
      
     synlinkGTK.ibidir.disconnect(synlinkGTK.chdict['ibidir'])


   def setDirection(self):

      try:

         inpeers = self.inObj.getPeers()

         if self.bidir:
            inpeers.append((0,self.outObj))
         else:
            for i in range(0,len(inpeers)):
               if inpeers[i][1] == self.outObj:
                  del inpeers[i]
         return True

      except:

         IMVEC.dbg.debug("linked item %s  doesn't have output, can't establish bidirectional link",(self.inObj),dbg.ERROR)
         return False


         

   def onBidirChanged(self,widget):
 
      if widget.get_active_text() == "False":
         self.bidir = False       
      else:
         self.bidir = True
  
      if not self.setDirection():
         self.bidir = False
         synlinkGTK.ibidir.set_active(0)
         

   def getPropWidget(self):

      if self.bidir == True:
         synlinkGTK.ibidir.set_active(1)
      else:
         synlinkGTK.ibidir.set_active(0)

      synlinkGTK.chdict['ibidir'] = synlinkGTK.ibidir.connect("changed",self.onBidirChanged)
      return synlinkGTK.o



class syncom(synobj):


   def __init__(self,name,text):

      self.init_common()
      self.text = text
      self.name = name
   def getText(self):

      return self.text

   def setText(self,text):

      self.text = text

   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       

        self.color = resclaleColorSel(ncolor.to_string())
        syncomGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()

   def onITextBufferChanged(self,textbuff):
      self.text = textbuff.get_text(textbuff.get_start_iter(),textbuff.get_end_iter())
      IMVEC.activeDoc.getContainer().getMember(self.id).getSynItem().setComment(self.text)


   def disconnectAll(self):
      syncomGTK.itextBuffer.disconnect(syncomGTK.chdict['iTextBuff'])
      syncomGTK.icolorBtn.disconnect(syncomGTK.chdict['icolorBtn'])

   def getPropWidget(self):

      syncomGTK.itextBuffer.set_text(self.text)
      syncomGTK.icolor.set_text(self.color)
      syncomGTK.chdict['iTextBuff'] = syncomGTK.itextBuffer.connect("changed",self.onITextBufferChanged)
      syncomGTK.chdict['icolorBtn'] = syncomGTK.icolorBtn.connect("clicked",self.onColorChange)

      return syncomGTK.o
      





class synmux(synobj):

   nbinst = 0


   def setIbuff(self,input_num,ibuff):
      self.buffs[input_num] = ibuff

   def init_run(self):

      self.alive = True
      self.buffs = ["","","","","",""]


   def run(self):

      
      while(self.alive):
        
         data_copy = self.data
         ctime = 0
         ready = 0

         for i in range (0,len(self.buffs)):
               if (self.buffs[i] != ""):
                  ready +=1
         while ( ready > 0 and ( (self.timeout == 0 and ready <6) or (ctime <= self.timeout or ready <6 ) ) ):
            ctime+=1
            #ready = 0     
            for i in range (0,len(self.buffs)):
               if (self.buffs[i] != ""):
                  ready +=1
            time.sleep(0.001)

         for i in range (0,len(self.buffs)):
            data_copy = data_copy.replace("[[SI%d]]"% (i),self.buffs[i].rstrip('\r').rstrip('\n')).replace("\\\n","\n").replace("\\\t","\t")
         
         if ready > 0:

            IMVEC.dbg.debug("MUXER %s BROADCASTING",(self),dbg.DEBUG)
            
            self.obuff = data_copy
            self.broadcast()
            self.obuff = ""
            self.buffs = ["","","","","",""]
            


   def __init__(self,name,data="[[SI0]] [[SI1]] [[SI2]] [[SI3]] [[SI4]] [[SI5]]",timeout=2000):

      synmux.nbinst+=1
      self.init_common()
      self.mInput = True
      self.name = name
      self.WOI = False
      self.data = data
      self.timeout = timeout
      
      self.ibuff = None
      self.obuff = ""
      self.peers=list()
      

   def getData(self):
      return self.data
   
   def getTimeout(self):
      return self.timeout
 
   
   def on_widget_changed(self,widget):
    
      if (widget == synmuxGTK.iname):
         self.name = widget.get_text()
      elif (widget == synmuxGTK.itimeout):
         #ICI METTRE CONTROL D'INT
         self.timeout = int(widget.get_text())
      elif (widget == synmuxGTK.idataBuffer):

         self.data = widget.get_text(widget.get_start_iter(),widget.get_end_iter())

        


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synmuxGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def getPropWidget(self):
    
      synmuxGTK.iname.set_text(self.name)
      synmuxGTK.icolor.set_text(self.color)
      synmuxGTK.itimeout.set_text(str(self.timeout))
      synmuxGTK.idataBuffer.set_text(self.data)
      
      synmuxGTK.chdict['iname'] = synmuxGTK.iname.connect("changed",self.on_widget_changed)
      synmuxGTK.chdict['icolorBtn'] = synmuxGTK.icolorBtn.connect("clicked",self.onColorChange)
      synmuxGTK.chdict['itimeout'] = synmuxGTK.itimeout.connect("changed",self.on_widget_changed)
      synmuxGTK.chdict['idata'] = synmuxGTK.idataBuffer.connect("changed",self.on_widget_changed)

      return synmuxGTK.o

   def disconnectAll(self):
      synmuxGTK.iname.disconnect( synmuxGTK.chdict['iname'])
      synmuxGTK.iname.disconnect( synmuxGTK.chdict['icolorBtn'])
      synmuxGTK.itimeout.disconnect(synmuxGTK.chdict['itimeout'])
      synmuxGTK.idataBuffer.disconnect(synmuxGTK.chdict['idata'])
         


class syndemux(synobj):

   nbinst = 0


   def updatePeers(self):
    
      del self.opeers[:]
      
      for i in range(0,6):

         self.opeers.append(list())

      for obj in IMVEC.activeDoc.getContainer().getSynObjects():
         
         if str(obj.__class__) == "synapseObjects.synlink" and obj.getOutObj() == self:
            
            self.opeers[obj.getOutputNum()].append((obj.getInputNum(),obj.getInObj()))

             
   def init_run(self):

      self.alive = True      
      self.separator = self.separator.replace("\\n","\n").replace("\\t","\t").replace("\\r","\r")


   def run(self):
      
         while (len(self.ibuff) != 0):

            input_buffer = self.ibuff.pop(0)

            (s0,s1,s2) = input_buffer.partition(":")
            input_buffer = s2

            del self.obuffs[:]

            pbuff = copy.copy(input_buffer)

            for i in range(0,5):
               (sep1,sep2,sep3) = pbuff.partition(self.separator)
               self.obuffs.append(sep1)
               if sep2 == "" and sep3 == "":
                  break
               pbuff = sep3

            if sep3 != "":

               self.obuffs.append(sep3)    
            self.bcast()
             

   def bcast(self):
   
      for i in range(0,len(self.obuffs)):
            
         #adds a line feed for each demuxed part
         try:
            if self.obuffs[i][len(self.obuffs[i])-1] != "\n":
               self.obuffs[i] +="\n"
         except:
            pass


         for peer in self.opeers[i]:

            (input_num, peerobj) = tuple(peer)         

            if (peerobj.mInput == True):
               IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuffs[i],peerobj.getName(),input_num),dbg.DEBUG)
               #peerobj.setIbuff(input_num,self.obuffs[i])
               peerobj.getIbuffs()[input_num].append("%d:%s" % (input_num,self.obuffs[i]) )
            else:

               if (peerobj.needSender == False):

                  IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuffs[i],peerobj.getName(),input_num),dbg.DEBUG)
                  #peerobj.setIbuff(str(input_num) + ":" +self.obuffs[i])
                  peerobj.getIbuff().append("%d:%s" % (input_num,self.obuffs[i]) )

               else:

                  IMVEC.dbg.debug("SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d",(self.obuffs[i],peerobj.getName(),input_num),dbg.DEBUG)
                  #peerobj.setIbuff(self.getName() + ":" + str(input_num) + ":" +self.obuffs[i])
                  peerobj.getIbuff().append("%s:%d:%s" % (self.getName(),input_num,self.obuff) )




   def __init__(self,name,separator="\\n"):

      syndemux.nbinst+=1
      self.init_common()
      self.name = name
      
      self.separator = separator
   
      self.obuffs = list()
      self.opeers = list()      

      self.ibuff = list()
      self.WOI = False

   
   def getSeparator(self):
      return self.separator
 


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        syndemuxGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)
        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()

   def on_widget_changed(self,widget):
    
      if (widget == syndemuxGTK.iname):
         self.name = widget.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(syndemuxGTK.iname.get_text())
      elif (widget == syndemuxGTK.iseparator):
         self.separator = widget.get_text()
     
   def disconnectAll(self):
      syndemuxGTK.iname.disconnect( syndemuxGTK.chdict['iname'])
      syndemuxGTK.iname.disconnect( syndemuxGTK.chdict['icolorBtn'])
      syndemuxGTK.iseparator.disconnect(syndemuxGTK.chdict['iseparator'])

   def getPropWidget(self):

      syndemuxGTK.iname.set_text(self.name)
      syndemuxGTK.icolor.set_text(self.color)
      syndemuxGTK.iseparator.set_text(self.separator)

      syndemuxGTK.chdict['iname'] = syndemuxGTK.iname.connect("changed",self.on_widget_changed)
      syndemuxGTK.chdict['icolorBtn'] = syndemuxGTK.icolorBtn.connect("clicked",self.onColorChange)
      syndemuxGTK.chdict['iseparator'] = syndemuxGTK.iseparator.connect("changed",self.on_widget_changed)

      return syndemuxGTK.o



class synmonitor(synobj):

   nbinst = 0



   def flush(self):

      IMVEC.activeDoc.getContainer().getMemberFromSynObj(self).getSynItem().flush()


   def updateDisplayBuffSize(self):
      return 0



   def init_run(self):

      self.alive = True
      self.fullContent = ""
      self.displayBuff = "" 

   def run(self):
 
         xref = IMVEC.activeDoc.getContainer().getMembers()[self.id].getSynItem()
         while (len(self.ibuff) != 0):

            input_buffer = self.ibuff.pop(0)
           
            IMVEC.dbg.debug("PROCESSED BUFF: %s" , (input_buffer),dbg.EXDEBUG)
            (input_num,sep,content) = input_buffer.partition(":")
            self.fullContent += content
            self.displayBuff = ""
            fclist = self.fullContent.split("\n")
            if len(fclist)-self.displayBuffSize < 0:
               init_var = 0
            else:
               init_var = len(fclist)-self.displayBuffSize

            for i in range (init_var,len(fclist)):
               self.displayBuff+= fclist[i] + "\n"
               
            #ici mettre la gestion de la taille de buffer suivant taille de monitor item
            gtk.gdk.threads_enter() 
            xref.setText(self.displayBuff)
            gtk.gdk.threads_leave()

            
         

         
   def __init__(self,name):

      self.init_common()

      synmonitor.nbinst += 1
      self.name = name
      self.WOI = False
      self.ibuff = list()
      self.obuff = ""
      self.fullContent = ""
      self.displayBuff = ""
      self.displayBuffSize = 10




   def disconnectAll(self):
     
      return 0

   def getPropWidget(self):

      return synmonitorGTK.o







class synpy(synobj):

   nbinst = 0


   def on_widget_changed(self,widget):

       if (widget == synpyGTK.iname):
         self.name = widget.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)
         
       elif (widget == synpyGTK.iwoi):
         #synapseHistory.history.addHistory()
         if synpyGTK.ipcuni.get_active_text() == "True":
            self.pcuni = True
         else:
            self.pcuni = False


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synpyGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)
        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()

   def init_run(self):

      self.alive = True

   def run(self):
 
         xref = IMVEC.activeDoc.getContainer().getMembers()[self.id].getSynItem()
         while (len(self.ibuff) != 0):

            input_buffer = self.ibuff.pop(0)
            (input_num,sep,content) = input_buffer.partition(":")
            content = content.rstrip("\r\n")
            #try:
            exec content
            #except:
               #IMVEC.dbg.debug("ISSUE WHILE EXECUTING PYTHON CODE BLOCK",tuple(),dbg.CRITICAL)
            

         
   def __init__(self,name):

      self.init_common()

      synpy.nbinst += 1
      self.name = name
      self.WOI = False
      self.ibuff = list()
      self.obuff = ""
      self.pcuni = False 
      

   def disconnectAll(self):
      synpyGTK.iname.disconnect( synpyGTK.chdict['iname'])
      synpyGTK.icolor.disconnect( synpyGTK.chdict['icolorBtn'])

   def getPropWidget(self):


      synpyGTK.iname.set_text(self.name)
      synpyGTK.icolor.set_text(self.color)
      
      
      synpyGTK.chdict['iname'] = synpyGTK.iname.connect("changed",self.on_widget_changed)
      synpyGTK.chdict['icolorBtn'] = synpyGTK.icolorBtn.connect("clicked",self.onColorChange)
      
      return synpyGTK.o



class synapp(synobj):

   nbinst = 0
  

   def init_run(self):

      self.alive = True
      runvars = dict()

      if (self.buffured_output):

         IMVEC.dbg.debug("SPAWNING PEXPECT PROCESS, OUTPUT BUFFURED MODE",tuple(),dbg.DEBUG)
         proc = pexpect.spawn(self.cmd)
      else:
         IMVEC.dbg.debug("SPAWNING PEXPECT PROCESS, OUTPUT UNBUFFURED MODE",tuple(),dbg.DEBUG)
         proc = pexpect.spawn(self.cmd,maxread=1)

      runvars['proc'] = proc
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)


   def run(self):
          
      proc = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()['proc']

      ## read pexpect process stdout and broadcast it
      self.obuff = ""
      try:
         self.obuff = proc.read_nonblocking(size=4096,timeout=0)
      except:
         pass

      
      if (self.obuff != ""): 

         if self.split_lines:
            splitted_list = list()
            splitted_list = self.obuff.split("\n")
            #IMVEC.dbg.debug("SPLITTED_LIST: %s",(splitted_list),dbg.EXDEBUG)
            for sp_line in splitted_list:
               if sp_line != "":
                  self.obuff = sp_line + "\n"
                  self.broadcast()
         else:
            self.broadcast()
         

      ## if input buffer not null, send to pexpect process stdin
      while (len(self.ibuff) != 0):
         input_buffer = self.ibuff.pop(0)
         (input_num,sep,content) = input_buffer.partition(":")
         IMVEC.dbg.debug("WRTIING TO %s STDIN",(self.name),dbg.DEBUG)

         proc.send(content)
            
      
           
                  
   def __init__(self,name,cmd="",keepalive=True):

      synapp.nbinst+=1
      self.init_common()

      self.WOI = True
      self.name = name

      self.cmd = cmd
      self.keepalive = keepalive
      self.peers = list()
      
      self.ibuff = list()
      self.obuff = ""
      self.buffured_output = False
      self.split_lines = False


   def getCmd(self):

      return self.cmd

   def setCmd(self,cmd):

      self.cmd = cmd

   def setKeepalive(self,async):

      self.async = keepalive

   def getKeepalive(self):

      return self.keepalive


   def onTextChange(self,widget):

      
      if (widget == synappGTK.iname):

         if synappGTK.iname.get_text()[len(synappGTK.iname.get_text())-1] == " ":
            synapseHistory.history.addHistory()

         self.name = synappGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(synappGTK.iname.get_text())
         #IMVEC.activeDoc.getActiveM().getSynItem().changeIOPos("right","left")


      elif (widget == synappGTK.irot):

         rotation = synappGTK.irot.get_active_text()
         if (rotation == "None"):
            IMVEC.activeDoc.getActiveM().getSynItem().setRotation(0)
         else:
            IMVEC.activeDoc.getActiveM().getSynItem().setRotation( int(rotation.replace(" Degrees","")) )
            IMVEC.activeDoc.getActiveM().getSynItem().rotate(self.rotation)


      elif (widget == synappGTK.icmd):

         if synappGTK.icmd.get_text()[len(synappGTK.icmd.get_text())-1] == " ":
            synapseHistory.history.addHistory()
         self.cmd = synappGTK.icmd.get_text()

      elif (widget == synappGTK.iwoi):
         #synapseHistory.history.addHistory()
         if synappGTK.iwoi.get_active_text() == "True":
            self.WOI = True
         else:
            self.WOI = False

      elif (widget == synappGTK.ibo):
         #synapseHistory.history.addHistory()
         if synappGTK.ibo.get_active_text() == "True":
            self.buffured_output = True
         else:
            self.buffured_output = False

      elif (widget == synappGTK.isl):
         #synapseHistory.history.addHistory()
         if synappGTK.isl.get_active_text() == "True":
            self.split_lines = True
         else:
            self.split_lines = False



   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synappGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()
         


   def disconnectAll(self):

         synappGTK.iname.disconnect(synappGTK.chdict['iname'])
         synappGTK.irot.disconnect(synappGTK.chdict['irot'])
         synappGTK.icmd.disconnect(synappGTK.chdict['icmd'])
         synappGTK.iwoi.disconnect(synappGTK.chdict['iwoi'])
         synappGTK.ibo.disconnect(synappGTK.chdict['ibo'])
         synappGTK.isl.disconnect(synappGTK.chdict['isl'])
         synappGTK.icolorBtn.disconnect(synappGTK.chdict['icolorBtn'])

   def getPropWidget(self):

      synappGTK.iname.set_text(self.name)
      synappGTK.icmd.set_text(self.cmd)
      synappGTK.icolor.set_text(self.color)

      if self.WOI == True:
         synappGTK.iwoi.set_active(0)
      else:
         synappGTK.iwoi.set_active(1)

      if self.buffured_output == True:
         synappGTK.ibo.set_active(0)
      else:
         synappGTK.ibo.set_active(1)

      if self.split_lines == True:
         synappGTK.isl.set_active(0)
      else:
         synappGTK.isl.set_active(1)

      synappGTK.chdict['iname'] = synappGTK.iname.connect("changed",self.onTextChange)
      synappGTK.chdict['irot'] = synappGTK.irot.connect("changed",self.onTextChange)
      synappGTK.chdict['icmd'] = synappGTK.icmd.connect("changed",self.onTextChange)
      synappGTK.chdict['iwoi'] = synappGTK.iwoi.connect("changed",self.onTextChange)
      synappGTK.chdict['ibo'] = synappGTK.ibo.connect("changed",self.onTextChange)
      synappGTK.chdict['isl'] = synappGTK.isl.connect("changed",self.onTextChange)
      synappGTK.chdict['icolorBtn'] = synappGTK.icolorBtn.connect("clicked",self.onColorChange)

      return synappGTK.o






class synfilter(synapp):


   def init_run(self):

      self.alive = True
      runvars = dict()
 
      if (self.filterType == "Simple Grep"):
         filterCmd = "grep " + self.data
      elif (self.filterType == "PCRE Grep"):
         filterCmd = "pcregrep " + self.data
      elif (self.filterType == "Sed Expression"):
         filterCmd = "sed " + self.data
      elif (self.filterType == "Awk Script"):
         filterCmd = "awk " + self.data

      IMVEC.dbg.debug("%s FILTERCMD: %s",(self,filterCmd),dbg.DEBUG)

      if (self.buffured_output):

         IMVEC.dbg.debug("SPAWNING PEXPECT PROCESS, OUTPUT BUFFURED MODE",tuple(),dbg.DEBUG)
         proc = pexpect.spawn(filterCmd)
      else:
         IMVEC.dbg.debug("SPAWNING PEXPECT PROCESS, OUTPUT UNBUFFURED MODE",tuple(),dbg.DEBUG)
         proc = pexpect.spawn(filterCmd,maxread=1)

      runvars['proc'] = proc
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)

       
   def __init__(self,name,filter_type="Simple Grep",data=""):

      self.init_common()
      self.name = name
      self.filterType = filter_type
      self.data = data
      self.WOI = False

      self.ibuff = list()
      self.obuff = ""

      self.peers = list()
      self.buffured_output = True
      self.split_lines = False


   def getFilterType(self):
      return self.filterType

   def getData(self):
      return self.data


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synfilterGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def on_widget_changed(self,widget):


      if (widget == synfilterGTK.iname):
         self.name = widget.get_text()

      elif (widget == synfilterGTK.ift):

         IMVEC.dbg.debug("SYNFILTER FILTERTYPE CHANGED",tuple(),dbg.DEBUG)

         self.filterType = widget.get_active_text()

      elif (widget == synfilterGTK.idataBuffer):

         IMVEC.dbg.debug("SYNFILTER DATA CHANGED",tuple(),dbg.DEBUG)
         self.data = synfilterGTK.idataBuffer.get_text(synfilterGTK.idataBuffer.get_start_iter(),synfilterGTK.idataBuffer.get_end_iter())


   def disconnectAll(self):
   
      synfilterGTK.iname.disconnect(synfilterGTK.chdict['iname'])
      synfilterGTK.icolorBtn.disconnect(synfilterGTK.chdict['icolorBtn'])
      synfilterGTK.ift.disconnect(synfilterGTK.chdict['ift'])
      synfilterGTK.idataBuffer.disconnect(synfilterGTK.chdict['idata']) 


  
   def getPropWidget(self):
  
      synfilterGTK.iname.set_text(self.name)
      synfilterGTK.icolor.set_text(self.color)
      synfilterGTK.idataBuffer.set_text(self.data)
      
      if (self.filterType == "Simple Grep"):
         synfilterGTK.ift.set_active(0)
      elif (self.filterType == "PCRE Grep"):
         synfilterGTK.ift.set_active(1)
      elif (self.filterType == "Sed Expression"):
         synfilterGTK.ift.set_active(2)
      elif (self.filterType == "Awk Script"):
         synfilterGTK.ift.set_active(3)        

      synfilterGTK.chdict['iname'] = synfilterGTK.iname.connect("changed",self.on_widget_changed)
      synfilterGTK.chdict['icolorBtn'] = synfilterGTK.icolorBtn.connect("clicked",self.onColorChange)
      synfilterGTK.chdict['ift'] = synfilterGTK.ift.connect("changed",self.on_widget_changed)
      synfilterGTK.chdict['idata'] = synfilterGTK.idataBuffer.connect("changed",self.on_widget_changed)
    
      return synfilterGTK.o





class syncli(synobj):

   nbinst = 0


   def sockConnect(self):

      (host,port) = self.connectInfos.split(":")

      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      try:
         sockfd.connect((host,int(port)))
      except: 
         IMVEC.dbg.debug("CANT CONNECT TO %s:%s",(host,port),dbg.ERROR)
         return -1

      fcntl(sockfd,F_SETFL,fcntl(sockfd,F_GETFL) | os.O_NONBLOCK)
      
      return sockfd

     

   def init_run(self):

      self.alive = True
      runvars = dict()
      sockfd = self.sockConnect()

      runvars['sockfd'] = sockfd
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)
 
      

   def run(self):
     
      sockfd = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()['sockfd']

      if (self.autoreco or sockfd != -1):

         self.sockConnect()

      (rr,wr,er) = select.select([sockfd],[],[],2)
      for fd in rr:    
         line = fd.recv(4096)
         if (line != ""):
            self.obuff = line
            self.broadcast() 
      
      if (len(self.ibuff) != 0 ):

         input_buffer = self.ibuff.pop(0)
         (input_num,sep,content) = input_buffer.partition(":")
         sockfd.send(content)
         

   def __init__(self,name,proto="Tcp",connectInfos="",keepalive=True):

      syncli.nbinst+=1
      self.init_common()

      self.name = name
      self.connectInfos = connectInfos
      self.keepalive = keepalive
      self.autoreco = True
      self.proto = proto
      self.WOI = False

      self.peers = list()
      
      self.ibuff = list()
      self.obuff = ""
  
   def getConnectInfos(self):

      return self.connectInfos

   def setConnectInfos(self,connectInfos):

      self.connectInfos = connectInfos

   def setKeepalive(self,async):

      self.async = keepalive

   def getKeepalive(self):

      return self.keepalive



   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        syncliGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def onTextChange(self,widget):


      if (widget == syncliGTK.iname):
         self.name = syncliGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(syncliGTK.iname.get_text())

      elif (widget == syncliGTK.ici):
         self.connectInfos = syncliGTK.ici.get_text()

      elif (widget == syncliGTK.iproto):

         self.proto = widget.get_active_text()
 

      elif (widget == syncliGTK.iar):
         if widget.get_active_text() == "True":
            self.autoreco = True 
        
         if widget.get_active_text() == "False":
            self.autoreco = False


   def disconnectAll(self):

         syncliGTK.iname.disconnect(syncliGTK.chdict['iname'])
         syncliGTK.icolorBtn.disconnect(syncliGTK.chdict['icolorBtn'])
         syncliGTK.ici.disconnect(syncliGTK.chdict['ici'])
         syncliGTK.iproto.disconnect(syncliGTK.chdict['iproto'])      
         syncliGTK.iar.disconnect(syncliGTK.chdict['iar']) 


   def getPropWidget(self):

      syncliGTK.iname.set_text(self.name)
      syncliGTK.icolor.set_text(self.color)
      syncliGTK.ici.set_text(self.connectInfos)


      if (self.proto == "Tcp"): 

         syncliGTK.iproto.set_active(0)
      else:
         syncliGTK.iproto.set_active(1)


      if (self.autoreco): 

         syncliGTK.iar.set_active(0)
      else:
         syncliGTK.iar.set_active(1)



      syncliGTK.chdict['iname'] = syncliGTK.iname.connect("changed",self.onTextChange)
      syncliGTK.chdict['icolorBtn'] = syncliGTK.icolorBtn.connect("clicked",self.onColorChange)
      syncliGTK.chdict['ici'] = syncliGTK.ici.connect("changed",self.onTextChange)
      syncliGTK.chdict['iproto'] = syncliGTK.iproto.connect("changed",self.onTextChange)      
      syncliGTK.chdict['iar'] = syncliGTK.iar.connect("changed",self.onTextChange) 


      return syncliGTK.o




class synreport(synobj):


   def getOutputFile(self):

      return self.output_file

   def setOutputFile(self):

      return self.output_file



   def onTextChange(self,widget):

      if (widget == synreportGTK.iname):
         self.name = synreportGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)

      elif (widget == synreportGTK.ifilename):
         self.output_file = synreportGTK.ifilename.get_text()
         

 
   def onFileChange(self,widget):

      dialog = gtk.FileChooserDialog(title="Save Report To...", parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK), backend=None)

      response = dialog.run()
      if response == gtk.RESPONSE_OK:
         savefile = dialog.get_filename()
         dialog.destroy()
         synreportGTK.ifilename.set_text(savefile)
         self.output_file = savefile

      elif response == gtk.RESPONSE_CANCEL:
         dialog.destroy()
         return




   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synreportGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def getPropWidget(self):

      synreportGTK.iname.set_text(self.name)
      synreportGTK.ifilename.set_text(self.output_file)
      synreportGTK.icolor.set_text(self.color)

      synreportGTK.chdict['icolorBtn'] = synreportGTK.icolorBtn.connect("clicked",self.onColorChange)
      synreportGTK.chdict['ibrowse'] = synreportGTK.ibrowse.connect("clicked",self.onFileChange)      
      synreportGTK.chdict['iname'] = synreportGTK.iname.connect("changed",self.onTextChange)
      synreportGTK.chdict['ifilename'] = synreportGTK.ifilename.connect("changed",self.onTextChange)

      return synreportGTK.o


   def disconnectAll(self):

      synreportGTK.icolorBtn.disconnect(synreportGTK.chdict['icolorBtn'])
      synreportGTK.ibrowse.disconnect(synreportGTK.chdict['ibrowse'])
      synreportGTK.iname.disconnect(synreportGTK.chdict['iname'])
      synreportGTK.ifilename.disconnect(synreportGTK.chdict['ifilename'])
      


   def __init__(self,name):

      self.init_common()

      self.buffersDict = dict()
      self.senders = list()

      self.name = name
      self.output_file = "synapse_report.pdf"
      self.WOI = False
      self.needSender = True
      self.color = "DEFAULT"

      self.textFont = "Helvetica"
      self.textFontSize = 10

      self.ibuff = list()
      self.obuff = None

   def kill(self):

      self.writeToPDF()
      self.alive = False


   def writeToPDF(self):

      #try:

         IMVEC.dbg.debug("writing %s to report",(self.pdfContent),dbg.EXDEBUG)

         pdf = SimpleDocTemplate(self.output_file)
         styles = getSampleStyleSheet()
         pdfcontent = list()

         date = strftime("Synapse Report -- generated on %Y-%m-%d %H:%M:%S")


         headerImg = Image(IMVEC.RES_PATH + "/images/synapse_rs.png")
         headerImg.drawWidth = .6 * headerImg.drawWidth
         headerImg.drawHeight = .6 * headerImg.drawHeight

         pdfcontent.append(headerImg)

         self.senders.sort()

         for sender in self.senders:

            pdfcontent.append(Spacer(0,inch*.1))
            pdfcontent.append(Paragraph(sender,styles['Heading1']))
            pdfcontent.append(Spacer(0,inch*.1))
            lines = self.buffersDict[sender].split("\n")

            for line in lines:

               pdfcontent.append(Paragraph(line,styles['Normal']))
               #pdfcontent.append(Spacer(0,inch*.1))

         pdfcontent.append(Spacer(0,inch*.4))
         pdfcontent.append(Paragraph(date,styles['Normal']))
         pdf.build(pdfcontent)



   def init_run(self):

      self.alive = True
      self.pdfContent = ""    
 
   def run(self):
 
       while (len(self.ibuff) != 0):
 
         input_buffer = self.ibuff.pop(0)

         (sender,sep,content0) = input_buffer.partition(":")
         (input_num,sep,content) = content0.partition(":")

         try:
            self.buffersDict[sender] += content
         except:
            self.buffersDict[sender] = content 
            self.senders.append(sender)


    
         




class syncontainer(synobj):


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        syncontainerGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()



   def onTextChange(self,widget):

      if (widget == syncontainerGTK.iname):
         self.name = syncontainerGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(syncontainerGTK.iname.get_text())


   def disconnectAll(self):

      syncontainerGTK.iname.disconnect(syncontainerGTK.chdict['iname'])
      syncontainerGTK.icolorBtn.disconnect(syncontainerGTK.chdict['icolorBtn'])


   def getPropWidget(self):

      syncontainerGTK.iname.set_text(self.name)
      syncontainerGTK.icolor.set_text(self.color)

      syncontainerGTK.chdict['iname'] = syncontainerGTK.iname.connect("changed",self.onTextChange)
      syncontainerGTK.chdict['icolorBtn'] = syncontainerGTK.icolorBtn.connect("clicked",self.onColorChange)

      return syncontainerGTK.o



   def appendObj(self,obj):

      self.objlist.append(obj)
     
 
   def getObjList(self):

      return self.objlist

   def flushObjList(self):

      del self.objlist[:]


   def updateObjList(self):

      self.objlist = list()

      self_canvas_ref = IMVEC.activeDoc.getContainer().getMemberFromSynObj(self).getSynItem().getO()
      for mid,member in IMVEC.activeDoc.getContainer().getMembers().items():
 
         if member.getSynItem().getO().get_property("parent") == self_canvas_ref:

            self.objlist.append(member.getSynObj())



   def __init__(self,name):

      self.name = name
      self.init_common()
      self.objlist = list()




class synlabel(synobj):


   def onTextChange(self,widget):

      if (widget == synlabelGTK.iname):
         self.name = synlabelGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)

      elif (widget == synlabelGTK.icrlf):
         if widget.get_active_text() == "True":
            self.crlf = True
         else:
            self.crlf = False

     
   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synlabelGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def getPropWidget(self):

      synlabelGTK.iname.set_text(self.name)
      synlabelGTK.icolor.set_text(self.color)
      
      if self.crlf:
         synlabelGTK.icrlf.set_active(0)
      else:
         synlabelGTK.icrlf.set_active(1)


      synlabelGTK.chdict['icolorBtn'] = synlabelGTK.icolorBtn.connect("clicked",self.onColorChange)
      synlabelGTK.chdict['iname'] = synlabelGTK.iname.connect("changed",self.onTextChange)
      synlabelGTK.chdict['icrlf'] = synlabelGTK.icrlf.connect("changed",self.onTextChange)
      
      return synlabelGTK.o


   def disconnectAll(self):

      synlabelGTK.icolorBtn.disconnect(synlabelGTK.chdict['icolorBtn'])
      synlabelGTK.iname.disconnect(synlabelGTK.chdict['iname'])
      synlabelGTK.icrlf.disconnect(synlabelGTK.chdict['icrlf'])


   def getContent(self):

      return self.content
      
   def setContent(self,content):
      self.content = content

   def __init__(self,name):

      self.init_common()
      self.peers = list()
      self.name = name
      self.WOI = False
      self.crlf = True

      self.ibuff = None
      self.obuff = ""
      self.content = ""


   def init_run(self):

     self.alive = True

   def run(self):

      if self.crlf:
         self.obuff = self.content.replace("\\n",'\n') + "\r\n"
      else:
         self.obuff = self.content.replace("\\n",'\n')

      self.broadcast()
      self.kill()


class synkbd(synobj):

   def onTextChange(self,widget):

      if (widget == synkbdGTK.iname):
         self.name = synkbdGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)


   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synkbdGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def getPropWidget(self):

      synkbdGTK.iname.set_text(self.name)
      synkbdGTK.icolor.set_text(self.color)
      
     
      synkbdGTK.chdict['icolorBtn'] = synkbdGTK.icolorBtn.connect("clicked",self.onColorChange)
      synkbdGTK.chdict['iname'] = synkbdGTK.iname.connect("changed",self.onTextChange)

      
      return synkbdGTK.o


   def disconnectAll(self):

      synkbdGTK.icolorBtn.disconnect(synkbdGTK.chdict['icolorBtn'])
      synkbdGTK.iname.disconnect(synkbdGTK.chdict['iname'])


   def setInputLock(self,ilock):

      self.ilock = ilock

   def getInputLock(self):

      return self.ilock

   def __init__(self,name):

      self.init_common()
      self.peers = list()
      self.name = name
      self.WOI = False

      self.ibuff = list()
      self.obuff = ""
      self.content = ""
      self.ilock = False
   

   def init_run(self):

      self.alive = True  

   def run(self):

      while (len(self.ibuff) != 0):

         self.obuff = self.ibuff.pop(0)

         self.broadcast()
         self.obuff = ""







class syndb(synobj):

   nbinst = 0
  

   def init_run(self):

      self.alive = True
      runvars = dict()
      
      try:
         (dbhost,dbport) = self.hostport.split(":")
      except:
         IMVEC.dbg.debug("CANNOT PARSE HOST:PORT PARAMETERS. STOPPING DB BLOCK",tuple(),dbg.CRITICAL)
         self.alive = False

      if (self.connec == "MySQL" ):

         IMVEC.dbg.debug("STARTING A NEW MYSQL CONNECTION",tuple(),dbg.DEBUG)
         dbh = MySQLdb.connect(host=dbhost,port=int(dbport),user=self.user,db=self.database,passwd=self.password)
         dbcurs = dbh.cursor()
         
      else:
         IMVEC.dbg.debug("STARTING A NEW POSTGRES CONNECTION",tuple(),dbg.DEBUG)
         dbh = psycopg2.connect(host=dbhost,port=int(dbport),user=self.user,db=self.database,passwd=self.password)
         dbcurs = dbh.cursor()
         
      runvars['dbh'] = dbh
      runvars['dbcurs'] = dbcurs
      
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)


   def run(self):

      dbcurs = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()['dbcurs']

      if (self.btype == "No Input"):

         dbcurs.execute(self.query)
         if (self.query.upper().find('INSERT') == 0  or self.query.upper().find('UPDATE') == 0 ):
               dbcurs.commit()
         results = dbcurs.fetchall()
         self.formatResults(results)

         self.alive = False

      else:

         while len(self.ibuff) != 0:

            input_buffer = self.ibuff.pop(0)
            (input_num,sep,content) = input_buffer.partition(":")
            nquery = self.query.replace("[[SYNDB_INPUT]]",content)
            dbcurs.execute(nquery)
 
            if (nquery.upper().find('INSERT') == 0  or nquery.upper().find('UPDATE') == 0 ):
               dbcurs.commit()
            results = dbcurs.fetchall()
            self.formatResults(results)
            
            


   def formatResults(self,results):

      if self.outputMode == "Split Lines":

         for line in results:

            self.obuff = ""
            for field in line:
               self.obuff  += str(field) + self.fieldSep
            self.broadcast()

      elif self.outputMode == "Split Fields":

         for line in results:
    
            for field in line:
               self.obuff = str(field)
               self.broadcast()


      elif self.outputMode == "Full Content":

         self.obuff = ""
         for line in results:
    
            for field in line:
               self.obuff  += str(field) + self.fieldSep
            self.obuff += "\n"

         self.broadcast()


            
   def __init__(self,name):

      synapp.nbinst+=1
      self.init_common()

      self.WOI = False
      self.name = name

      self.query ="select * from [[SYNDB_INPUT]] limit 1"

      self.peers = list()
      self.ibuff = list()
      self.obuff = ""
      self.connec = "MySQL"
      self.btype = "No Input"
      self.hostport="127.0.0.1:3306"
      self.database = ""
      self.user = ""
      self.password = ""
      self.outputMode = "Split Lines"
      self.fieldSep = "|"
      
      
      
   def getQuery(self):

      return self.query

   def setQuery(self,query):

      self.query = query

   def setConnector(self,connector):

      self.connector = connector

   def getConnector(self):

      return self.connector

         

   def onITextBufferChanged(self,textbuff):
      self.query = textbuff.get_text(textbuff.get_start_iter(),textbuff.get_end_iter())

   def onTextChange(self,widget):


      if (widget == syndbGTK.iname):

         self.name = syndbGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)
         #IMVEC.activeDoc.getActiveM().getSynItem().changeIOPos("right","left")


      elif (widget == syndbGTK.ihostport):
         self.hostport = syndbGTK.ihostport.get_text()

      elif (widget == syndbGTK.idb):
         self.database = syndbGTK.idb.get_text()
         
      elif (widget == syndbGTK.iuser):
         self.user = syndbGTK.iuser.get_text()

      elif (widget == syndbGTK.ipassword):
         self.password = syndbGTK.ipassword.get_text()      


      elif (widget == syndbGTK.ibtype):
         if syndbGTK.ibtype.get_active_text() == "No Input":
            self.btype = "No Input"
            IMVEC.activeDoc.getActiveM().getSynItem().setInput(False)
         else:
            self.btype = "Has Input"
            IMVEC.activeDoc.getActiveM().getSynItem().setInput(True)

      elif (widget == syndbGTK.iconnec):
         if syndbGTK.iconnec.get_active_text() == "MySQL":
            self.connec = "MySQL"
         else:
            self.connec = "Postgres"

      elif (widget == syndbGTK.iomode):
         self.outputMode = syndbGTK.iomode.get_active_text()

      elif (widget == syndbGTK.isep):
         self.fieldSep = syndbGTK.isep.get_text()



        
   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synappGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()
         


   def disconnectAll(self):

         for key,value in syndbGTK.chdict.items():

            exec "syndbGTK.%s.disconnect(%d)" % (key,value)




   def getPropWidget(self):

      syndbGTK.iname.set_text(self.name)
      syndbGTK.ihostport.set_text(self.hostport)
      syndbGTK.idb.set_text(self.database)
      syndbGTK.iuser.set_text(self.user)
      syndbGTK.ipassword.set_text(self.password)
      syndbGTK.isep.set_text(self.fieldSep)
      
      syndbGTK.icolor.set_text(self.color)

      syndbGTK.itextBuffer.set_text(self.query)


      if self.connec == "MySQL":
         syndbGTK.iconnec.set_active(0)
      else:
         syndbGTK.iconnec.set_active(1)


      if self.outputMode == "Full Content":
         syndbGTK.iomode.set_active(0)
      elif self.outputMode == "Split Lines":
         syndbGTK.iomode.set_active(1)
      else:
         syndbGTK.iomode.set_active(2)


      if self.btype == "No Input":
         syndbGTK.ibtype.set_active(0)
      else:
         syndbGTK.ibtype.set_active(1)
  
      syndbGTK.chdict['iname'] = syndbGTK.iname.connect("changed",self.onTextChange)
      syndbGTK.chdict['icolorBtn'] = syndbGTK.icolorBtn.connect("clicked",self.onColorChange)
      syndbGTK.chdict['iconnec'] = syndbGTK.iconnec.connect("changed",self.onTextChange)
      syndbGTK.chdict['ibtype'] = syndbGTK.ibtype.connect("changed",self.onTextChange)
      syndbGTK.chdict['idb'] = syndbGTK.idb.connect("changed",self.onTextChange)
      syndbGTK.chdict['iuser'] = syndbGTK.iuser.connect("changed",self.onTextChange)
      syndbGTK.chdict['ipassword'] = syndbGTK.ipassword.connect("changed",self.onTextChange)
      syndbGTK.chdict['iomode'] = syndbGTK.iomode.connect("changed",self.onTextChange)
      syndbGTK.chdict['isep'] = syndbGTK.isep.connect("changed",self.onTextChange)
      syndbGTK.chdict['itextBuffer'] = syndbGTK.itextBuffer.connect("changed",self.onITextBufferChanged)

      return syndbGTK.o












class synxmpp(synobj):

   nbinst = 0
  

   def msgHandler(self,session,message):


      content = message.getBody()
      if content != None:
         self.obuff = content
         if (self.crlf):
            self.obuff += "\r\n"
         self.broadcast()

   def init_run(self):

      self.alive = True
      runvars = dict()
      
      try:
         (host,port) = self.hostport.split(":")
         port = int(port)
         print "Using %s:%d" %(host,port)
      except:
         host = None
         port = None
         print "No HOST/PORT PROVIDED"
         pass
    
  
      IMVEC.dbg.debug("STARTING A NEW XMPP CLIENT",tuple(),dbg.DEBUG)

      jid = xmpp.protocol.JID(self.jid)
      client = xmpp.Client(jid.getDomain(), debug=[])
      client.connect()
      client.auth(jid.getNode(), self.password)
      client.sendInitPresence()
      client.RegisterHandler('message',self.msgHandler)
  
      
      runvars['client'] = client
      #runvars['dbcurs'] = dbcurs
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)


   def run(self):

      runvars = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()
      client = runvars['client']
      client.Process()

      while len(self.ibuff) != 0:

         input_buffer = self.ibuff.pop(0)
         (input_num,sep,content) = input_buffer.partition(":")

         for jid in self.jidpeers:
            client.send(xmpp.protocol.Message(jid,content))      

      return
    
          
   def __init__(self,name):

      synxmpp.nbinst+=1
      self.init_common()

      self.WOI = False
      self.name = name

    
      self.peers = list()
      self.ibuff = list()
      self.obuff = ""

      self.jid = "foo@bar.com"
      self.password = ""
      self.hostport = ""
      self.crlf = True
      self.jidpeers = list()
      


   def onITextBufferChanged(self,textbuff):
     jpcontent = textbuff.get_text(textbuff.get_start_iter(),textbuff.get_end_iter())

     self.jidpeers = jpcontent.split("\n")

     for i in range(0,len(self.jidpeers)):
        if self.jidpeers[i].find('@') <= 0:
           del self.jidpeers[i]



   def onTextChange(self,widget):


      if (widget == synxmppGTK.iname):

         self.name = syndbGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)
         #IMVEC.activeDoc.getActiveM().getSynItem().changeIOPos("right","left")


      elif (widget == synxmppGTK.ihostport):
         self.hostport = synxmppGTK.ihostport.get_text()

      elif (widget == synxmppGTK.ijid):
         self.jid = synxmppGTK.ijid.get_text()
         
     
      elif (widget == synxmppGTK.ipassword):
         self.password = synxmppGTK.ipassword.get_text()      


      elif (widget == synxmppGTK.icrlf):
         if synxmppGTK.icrlf.get_active_text() == "False":
            self.crlf = False
         else:
            self.crlf = True


     
   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synappGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()
         


   def disconnectAll(self):

         for key,value in synxmppGTK.chdict.items():

            exec "synxmppGTK.%s.disconnect(%d)" % (key,value)




   def getPropWidget(self):

      synxmppGTK.iname.set_text(self.name)
      synxmppGTK.ihostport.set_text(self.hostport)
      synxmppGTK.ijid.set_text(self.jid)
      synxmppGTK.ipassword.set_text(self.password)

      synxmppGTK.icolor.set_text(self.color)

      jidcontent = ""
      for jid in self.jidpeers:
         jidcontent += jid + "\n"
      synxmppGTK.itextBuffer.set_text(jidcontent)
  

     
      synxmppGTK.chdict['iname'] = synxmppGTK.iname.connect("changed",self.onTextChange)
      synxmppGTK.chdict['icolorBtn'] = synxmppGTK.icolorBtn.connect("clicked",self.onColorChange)
      synxmppGTK.chdict['ihostport'] = synxmppGTK.ihostport.connect("changed",self.onTextChange)
      synxmppGTK.chdict['ijid'] = synxmppGTK.ijid.connect("changed",self.onTextChange)
      synxmppGTK.chdict['ipassword'] = synxmppGTK.ipassword.connect("changed",self.onTextChange)
      synxmppGTK.chdict['icrlf'] = synxmppGTK.icrlf.connect("changed",self.onTextChange)
      synxmppGTK.chdict['itextBuffer'] = synxmppGTK.itextBuffer.connect("changed",self.onITextBufferChanged)


      #synxmppGTK.chdict['ijidpeers'] = syndbGTK.iomode.connect("changed",self.onTextChange)

      

      return synxmppGTK.o






class synscapy(synobj):

   nbinst = 0
  

   def init_run(self):

      self.alive = True
      runvars = dict()
      
      try:
         (dbhost,dbport) = self.hostport.split(":")
      except:
         IMVEC.dbg.debug("CANNOT PARSE HOST:PORT PARAMETERS. STOPPING DB BLOCK",tuple(),dbg.CRITICAL)
         self.alive = False

      if (self.connec == "MySQL" ):

         IMVEC.dbg.debug("STARTING A NEW MYSQL CONNECTION",tuple(),dbg.DEBUG)
         dbh = MySQLdb.connect(host=dbhost,port=int(dbport),user=self.user,db=self.database,passwd=self.password)
         dbcurs = dbh.cursor()
         
      else:
         IMVEC.dbg.debug("STARTING A NEW POSTGRES CONNECTION",tuple(),dbg.DEBUG)
         dbh = psycopg2.connect(host=dbhost,port=int(dbport),user=self.user,db=self.database,passwd=self.password)
         dbcurs = dbh.cursor()
         
      runvars['dbh'] = dbh
      runvars['dbcurs'] = dbcurs
      
      IMVEC.activeDoc.getContainer().getMembers()[self.id].setRunVars(runvars)


   def run(self):

      dbcurs = IMVEC.activeDoc.getContainer().getMembers()[self.id].getRunVars()['dbcurs']

      if (self.btype == "No Input"):

         dbcurs.execute(self.query)
         if (self.query.upper().find('INSERT') == 0  or self.query.upper().find('UPDATE') == 0 ):
               dbcurs.commit()
         results = dbcurs.fetchall()
         self.formatResults(results)

         self.alive = False

      else:

         while len(self.ibuff) != 0:

            input_buffer = self.ibuff.pop(0)
            (input_num,sep,content) = input_buffer.partition(":")
            nquery = self.query.replace("[[SYNDB_INPUT]]",content)
            dbcurs.execute(nquery)
 
            if (nquery.upper().find('INSERT') == 0  or nquery.upper().find('UPDATE') == 0 ):
               dbcurs.commit()
            results = dbcurs.fetchall()
            self.formatResults(results)
            
            


   def formatResults(self,results):

      if self.outputMode == "Split Lines":

         for line in results:

            self.obuff = ""
            for field in line:
               self.obuff  += str(field) + self.fieldSep
            self.broadcast()

      elif self.outputMode == "Split Fields":

         for line in results:
    
            for field in line:
               self.obuff = str(field)
               self.broadcast()


      elif self.outputMode == "Full Content":

         self.obuff = ""
         for line in results:
    
            for field in line:
               self.obuff  += str(field) + self.fieldSep
            self.obuff += "\n"

         self.broadcast()


            
   def __init__(self,name):

      synapp.nbinst+=1
      self.init_common()

      self.WOI = False
      self.name = name

      self.query ="select * from [[SYNDB_INPUT]] limit 1"

      self.peers = list()
      self.ibuff = list()
      self.obuff = ""

      self.btype = "No Input"
      self.expr = ""
      
      
      
   def getQuery(self):

      return self.query

   def setQuery(self,query):

      self.query = query

   def setConnector(self,connector):

      self.connector = connector

   def getConnector(self):

      return self.connector

         

   def onITextBufferChanged(self,textbuff):
      self.expr = textbuff.get_text(textbuff.get_start_iter(),textbuff.get_end_iter())

   def onTextChange(self,widget):


      if (widget == synscapyGTK.iname):

         self.name = synscapyGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(self.name)
         #IMVEC.activeDoc.getActiveM().getSynItem().changeIOPos("right","left")


      elif (widget == synscapyGTK.ibtype):
         if synscapyGTK.ibtype.get_active_text() == "No Input":
            self.btype = "No Input"
            IMVEC.activeDoc.getActiveM().getSynItem().setInput(False)
         else:
            self.btype = "Has Input"
            IMVEC.activeDoc.getActiveM().getSynItem().setInput(True)

  
   def onColorChange(self,widget):

      colorseldlg = gtk.ColorSelectionDialog('Choose a new color for building block')
      colorsel = colorseldlg.colorsel

      response = colorseldlg.run()
   	
      if response == gtk.RESPONSE_OK:
        ncolor = colorsel.get_current_color()
       
        self.color = resclaleColorSel(ncolor.to_string())
        synscapyGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()
         


   def disconnectAll(self):

         for key,value in synscapyGTK.chdict.items():

            exec "synscapyGTK.%s.disconnect(%d)" % (key,value)




   def getPropWidget(self):

      synscapyGTK.iname.set_text(self.name)
      synscapyGTK.icolor.set_text(self.color)
      synscapyGTK.itextBuffer.set_text(self.expr)

      if self.btype == "No Input":
         synscapyGTK.ibtype.set_active(0)
      else:
         synscapyGTK.ibtype.set_active(1)

  
      synscapyGTK.chdict['iname'] = synscapyGTK.iname.connect("changed",self.onTextChange)
      synscapyGTK.chdict['icolorBtn'] = synscapyGTK.icolorBtn.connect("clicked",self.onColorChange)
      synscapyGTK.chdict['ibtype'] = synscapyGTK.ibtype.connect("changed",self.onTextChange)
      synscapyGTK.chdict['itextBuffer'] = synscapyGTK.itextBuffer.connect("changed",self.onITextBufferChanged)

      return synscapyGTK.o









class synsel:


   def unselect(self):

      for item in self.selectedItems:
         
         (nx,ny) = getAbsoluteCoords(IMVEC.activeDoc.getRootItem(),item.getO(),0,0)
         item.getO().set_property("parent",IMVEC.activeDoc.getRootItem())
         item.getO().set_property("x",nx)
         item.getO().set_property("y",ny)

         item.getMF().set_property("stroke_color","#cccccc")
         item.connectMF()      

      self.selectedItems = list()
   

   def getSelectedItems(self):

      return self.selectedItems

   def isEmpty(self):

      if len(self.selectedItems) == 0 : return True
      return False

   def __init__(self):

      self.selectedItems = list()

