#!/usr/bin/env python

import gtk
#import glib
import goocanvas

import sys
sys.path.append("/usr/lib/synapse")
from synapseIMVEC import *
from synapseGTKProperties import *
from synapseUtils import *

from subprocess import Popen, PIPE
from fcntl import fcntl , F_GETFL, F_SETFL
import select
import signal
import os
import time
import copy
import socket
import pexpect


#class to embbed and manipulate synlinker objects
class container:

   def __init__(self):
      self.members = dict()

   def append(self,member):

      self.members[member.getSynObj().getName()] = member

   def getMember(self,name):

      return self.members[name]


   def delete(self,dmember):

      print "DELEtE METHOD CALLED WITH OBJ:", dmember

      for mname,member in self.members.items():

         if member == dmember:
               print "DELETING MEMBER:",member
               member.getSynObj().delete()
               del self.members[mname]
               
                
   def getMemberFromSynItem(self,synItem):
      for  mname,member in self.members.items():
         if (member.getSynItem() == synItem):
            return member
            break


   def getMemberFromSynObj(self,synObj):
      for  mname,member in self.members.items():
         if (member.getSynObj() == synObj):
            return member
            break


   def getMembers(self):

      return self.members


   def updatePeers(self):
      for obj in self.getSynObjects():
         obj.updatePeers()


   def getSynObjects(self):

      objList = list()
      for  mname,member in self.members.items():
         objList.append(member.getSynObj())
      return objList

   def getSynItems(self):

      itemList = list()
      for mname,member in self.members.items():
         itemList.append(member.getSynItem())
      return itemList


   def getSynItem(self,synObj):

      for mname,member in self.members.items():
         print member
         if (member.getSynObj() == synObj):
            return member.getSynItem()
            break

   def getSynObj(self,synItem):
     
      for mname,member in self.members.items():
         print member
         if (member.getSynItem() == synItem):
            return member.getSynObj()
            break



# class that makes the link between synapse objects and synapse canvas items
class linker(object):


   def __init__(self,synObject,synItem):

      self.synObject = synObject
      self.synItem = synItem
      
   def setSynObj(self,synObject):

      self.synObject = synObject

   def setSynItem(self,synItem):

      self.synItem = synItem

   def getSynObj(self):

      return self.synObject

   def getSynItem(self):

      return self.synItem

   def updateSynObjCanvasProperties(self):

      canvasProperties = tuple()

      if (str(self.synItem.getO().__class__) != "goocanvas.Path" ):
         x = self.synItem.getO().get_property("x")
         y = self.synItem.getO().get_property("y")      
         width = self.synItem.getO().get_property("width")
         height = self.synItem.getO().get_property("height")
         mfwidth = self.synItem.getMF().get_property("width")
         mfheight = self.synItem.getMF().get_property("height")
         canvasProperties = (x,y,width,height,mfwidth,mfheight)

      else:
         data = self.synItem.getO().get_property("data")
         canvasProperties = (data)

      self.synObject.setCanvasProperties(canvasProperties)



class synobj:

   nbinst = 0


   def delete(self):

      del self

   def kill(self):
      self.alive = False


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
     
   def broadcast(self):

      for peer in self.peers:

         (input_num, peerobj) = tuple(peer)         

         if (peerobj.mInput == True):
            print "SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d" % (self.obuff,peerobj.getName(),input_num)
            peerobj.setIbuff(input_num,self.obuff)
  
         else:
            print "SENDING MESSAGE \"%s\" TO %s, INPUT NUM %d" % (self.obuff,peerobj.getName(),input_num)
            peerobj.setIbuff(str(input_num) + ":" +self.obuff)

      self.ibuff = ""

   #method to override for each building block
   def run(self):
      return 0

   def __init__(self,name):
      
      self.name = name
      synobj.nbinst+=1
      return self 
  
   def getName(self):

      return self.name   

   def setName(self,name):

      self.name = name

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
 
      for obj in IMVEC.activeDoc.getContainer().getSynObjects():
         
         if str(obj.__class__) == "synapseObjects.synlink":
            if obj.getOutObj() == self and obj.getOutputNum() == 0:
               print "UPDATING LINK FOR ", self
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


      self.title = title
      self.author = author
      self.date = date
      self.descr = descr
      self.color="DEFAULT"
   
    
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



class synfilter(synobj):


   def run(self):

      if (self.filterType == "Simple Grep"):
         filterCmd = "grep --line-buffered " + self.data
      elif (self.filterType == "PCRE Grep"):
         filterCmd = "pcregrep " + self.data
      elif (self.filterType == "Sed Expression"):
         filterCmd = "sed -u " + self.data
      elif (self.filterType == "Awk Script"):
         filterCmd = "awk " + self.data

      self.alive = True

      print "FILTERCMD:",filterCmd

     

      proc = Popen(filterCmd, shell=True, stdout=PIPE,stdin=PIPE,bufsize=4096)
      fcntl(proc.stdout,F_SETFL,fcntl(proc.stdout,F_GETFL) | os.O_NONBLOCK)
      fcntl(proc.stdin,F_SETFL,fcntl(proc.stdin,F_GETFL) | os.O_NONBLOCK)            
      
      line = ""

      while(proc.returncode == None and self.alive):
         
         proc.poll()
         (rr,wr,er) = select.select([proc.stdout],[],[],0)
         
         for fd in rr:    
            line = fd.read()
            if (line != ""):
               self.obuff = line 
               self.broadcast() 
            
         if (self.ibuff != ""):
            print "WRITING IBUFF TO FILTER"
            (input_num,sep,content) = self.ibuff.partition(":")
            proc.stdin.write(content)
            proc.stdin.flush()
            proc.stdout.flush()
            #proc.stdin.close()
            self.ibuff = ""
       
           
      try:
         proc.kill()
      except:
         print "subprocess already closed",self   
         print "return code:", proc.returncode  
     

   def __init__(self,name,filter_type="Simple Grep",data=""):

      self.name = name
      self.filterType = filter_type
      self.data = data
      self.color="DEFAULT"
 
      self.alive = False
      self.mInput = False
      self.ibuff = ""
      self.obuff = ""

      self.peers = list()


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
         print "FT CHANGED"
         self.filterType = widget.get_active_text()

      elif (widget == synfilterGTK.idataBuffer):

         print "DATA CHANGED"
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

  
class syntimer(synobj):


   def run(self):
     
      self.alive = True
      buff_repeat = ""

      while(self.alive == True):
         time.sleep(float(int(self.interval)/1000))
         
         if (buff_repeat != ""):
            print "BCASTING ", buff_repeat            
            self.obuff = buff_repeat
            self.broadcast() 

         if (self.ibuff != ""):
            (input_num,sep,content) = self.ibuff.partition(":")
            print "%s IBUFF: %s" % (self.name,content) 
            #time.sleep(float(int(self.interval)/1000))

            if (self.loop == False): 
               buff_repeat = ""      
            else:
               buff_repeat = copy.copy(content)
               print "KEEPING BUFFER FOR FURTHER USAGE"
           
            self.obuff = content
            self.broadcast()

          
   def __init__(self,name,interval=1000,loop=False):

      self.name = name
      self.interval = interval
      self.loop = loop
      self.color="DEFAULT"

      self.ibuff = ""
      self.obuff = ""
      self.mInput = False

      self.peers= list()

   def getPeriod(self):
      return self.interval

   def getLoop(self):
      return self.loop


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

      elif (widget == syntimerGTK.iinterval):
         self.interval = widget.get_text()

      elif (widget == syntimerGTK.iloop):
      
         if (widget.get_active_text() == "False"):   
            self.loop = False
         else:
            self.loop = True


   
   def disconnectAll(self):

      syntimerGTK.iname.disconnect(syntimerGTK.chdict['iname'])
      syntimerGTK.icolorBtn.disconnect(syntimerGTK.chdict['icolorBtn'])
      syntimerGTK.iinterval.disconnect(syntimerGTK.chdict['iinterval'])      
      syntimerGTK.iloop.disconnect(syntimerGTK.chdict['iloop'])    

   def getPropWidget(self):


      syntimerGTK.iname.set_text(self.name)
      syntimerGTK.icolor.set_text(self.color)
      syntimerGTK.iinterval.set_text(str(self.interval))

      if self.loop == True:
         syntimerGTK.iloop.set_active(1)
      else:
         syntimerGTK.iloop.set_active(0)


      syntimerGTK.chdict['iname'] = syntimerGTK.iname.connect("changed",self.on_widget_changed)
      syntimerGTK.chdict['icolorBtn'] = syntimerGTK.icolorBtn.connect("clicked",self.onColorChange)
      syntimerGTK.chdict['iinterval'] = syntimerGTK.iinterval.connect("changed",self.on_widget_changed)      
      syntimerGTK.chdict['iloop'] = syntimerGTK.iloop.connect("changed",self.on_widget_changed)  


      
      return syntimerGTK.o



class synjector(synobj):


   def __init__(self,name,injectType="string",data="",linesPerBlock=1,loop=False,fileName=""):

      self.name = name
      self.color="DEFAULT"
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

   def __init__(self,name,testType="string_cmp"):

      syntest.nbinst+=1

      self.name = name
      self.color="DEFAULT"
      self.testType = testType
      
      self.peers = list()
      self.peersFalse = list()      
   
  
   def setPeersFalse(self,pfalse):

      self.peersFalse = pfalse

   def getPeersFalse(self):
      return self.peersFalse

   def getTestType(self):
      return self.testType

   def getPropWidget(self):

      return syntestGTK.o



class synlink(synobj):

   def __init__(self,name,outObj,inObj):

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

   def onBidirChanged(self,widget):
      
      if widget.get_active_text() == "False":
         self.bidir = False
      else:
         self.bidir = True

   
   def getPropWidget(self):

      if self.bidir == True:
         synlinkGTK.ibidir.set_active(1)
      else:
         synlinkGTK.ibidir.set_active(0)

      synlinkGTK.chdict['ibidir'] = synlinkGTK.ibidir.connect("changed",self.onBidirChanged)
      return synlinkGTK.o



class syncom(synobj):


   def __init__(self,name,text):

      self.text = text
      self.name = name
      self.color="DEFAULT"
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
      IMVEC.activeDoc.getContainer().getMember(self.name).getSynItem().setComment(self.text)


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

   def run(self):

      self.alive = True

      self.buffs = ["","","","","",""]

      
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
            data_copy = data_copy.replace("[[SI%d]]"% (i),self.buffs[i].rstrip('\n'))
         
         if ready > 0:
            print "BROADCASTING"
            self.obuff = data_copy
            self.broadcast()
            self.obuff = ""
            self.buffs = ["","","","","",""]
            



   def __init__(self,name,data="[[SI0]] [[SI1]] [[SI2]] [[SI3]] [[SI4]] [[SI5]]",timeout=2000):

      synmux.nbinst+=1
      self.name = name
      self.color="DEFAULT"
      self.data = data
      self.timeout = timeout
      
      self.ibuff = ""
      self.obuff = ""
      self.alive = False
      self.mInput = True
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
         self.timeout = widget.get_text()
      elif (widget == synmuxGTK.idataBuffer):

         self.data = synmuxGTK.idataBuffer.get_text()


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
            
            self.opeers[obj.getOutputNum()].append(obj.getInObj())

             
   def run(self):

      self.alive = True
      
      self.separator = self.separator.replace("\\n","\n").replace("\\t","\t").replace("\\r","\r")
      
      while(self.alive == True):
      
         if (self.ibuff != ""):
            del self.obuffs[:]
            print "DEMUX IBUFF:",self.ibuff
            pbuff = copy.copy(self.ibuff)
            for i in range(0,5):
               (sep1,sep2,sep3) = pbuff.partition(self.separator)
               print sep1
               print "==="
               print sep3
               pbuff = sep3
               self.obuffs.append(sep1)
            self.obuffs.append(sep3)

            self.bcast()
            self.ibuff = ""
             

   def bcast(self):
   
      for i in range(0,6):
            
         for peer in self.opeers[i]:
            if self.obuffs[i][len(self.obuffs[i])-1] != "\n":
               self.obuffs[i] +="\n"
  
            peer.setIbuff(self.obuffs[i])
      
   def __init__(self,name,separator="\\n"):

      syndemux.nbinst+=1
      self.name = name
      self.color="DEFAULT"
      self.separator = separator
   
      self.obuffs = list()
      self.opeers = list()      

      self.ibuff = ""
      self.mInput = False
      self.alive = False


   
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


   def updateDisplayBuffSize(self):
      return 0


   def run(self):
     
      self.alive = True
      xref = IMVEC.activeDoc.getContainer().getMemberFromSynObj(self).getSynItem()
      self.fullContent = ""
      self.displayBuff = ""     

      while(self.alive == True):
         if (self.ibuff != ""):
            (input_num,sep,content) = self.ibuff.partition(":")
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
            self.ibuff = ""


   def __init__(self,name):
      synmonitor.nbinst += 1
      self.name = name
      self.WOI = True
      self.color="DEFAULT"
      
      self.ibuff = ""
      self.obuff = ""

      self.fullContent = ""
      self.displayBuff = ""
      self.displayBuffSize = 10
      self.alive = False
      self.mInput = False

   def disconnectAll(self):
      return 0

   def getPropWidget(self):

      return synmonitorGTK.o


class synapp(synobj):

   nbinst = 0
  

   def updatePeers(self):
    
      del self.peers[:]
      
      for obj in IMVEC.activeDoc.getContainer().getSynObjects():
         
         if str(obj.__class__) == "synapseObjects.synlink":
            if obj.getOutObj() == self and obj.getOutputNum() == 0:
               print "UPDATING LINK FOR ", self
               self.peers.append([obj.getInputNum(),obj.getInObj()])
            elif obj.getOutObj() == self and obj.getOutputNum() == 1:
               print "UPDATING LINK FOR ", self
               self.peersSTDERR.append([obj.getInputNum(),obj.getInObj()])

   def bcastSTDERR(self):

      for peer in self.peersSTDERR:

         (input_num, peerobj) = tuple(peer)  

         print "SENDING ERR MESSAGE \"%s\" TO %s" % (self.obuff2,peerobj.getName())
         peerobj.setIbuff(self.obuff2)

      #self.ibuff = ""

   def run(self):
          
      self.alive = True
  

      proc = pexpect.spawn(self.cmd)


      #proc = Popen(self.cmd, shell=True, stdout=PIPE,stdin=PIPE,stderr=PIPE,bufsize=4096)
      #fcntl(proc.stdout,F_SETFL,fcntl(proc.stdout,F_GETFL) | os.O_NONBLOCK)
      #fcntl(proc.stdin,F_SETFL,fcntl(proc.stdin,F_GETFL) | os.O_NONBLOCK)            
      #fcntl(proc.stderr,F_SETFL,fcntl(proc.stderr,F_GETFL) | os.O_NONBLOCK) 
 
      line = ""
      lineErr = ""
      while(self.alive):

         self.obuff = ""
         try:
            self.obuff = proc.read_nonblocking(size=4096,timeout=1)
         except:
            pass

         if (self.obuff != ""):            
            self.broadcast()
         
         #proc.poll()

         #(rr,wr,er) = select.select([proc.stdout],[proc.stdin],[proc.stderr],0)
         #for fd in rr:    
            #line = fd.read()
            #if (line != ""):
               #self.obuff = line 
               #self.broadcast() 
            
         #try:
            #lineErr = proc.stderr.read()
            #if (lineErr != ""):
               #self.obuff2 = lineErr 
               #self.bcastSTDERR()
         #except:
             #pass




         if (self.ibuff != ""):
            (input_num,sep,content) = self.ibuff.partition(":")
            print "WRTIING TO %s STDIN" % (self.name)
            proc.send(content)
            #proc.sendeof()
            #proc.stdin.write(content)
            #proc.stdin.flush()
            #self.ibuff = ""
            
      try:
         #proc.kill()
         pass
      except:
         print "subprocess already closed",self   
         print "return code:", proc.returncode

   def __init__(self,name,cmd="",keepalive=True):

      synapp.nbinst+=1

      self.WOI = True
      self.name = name
      self.color="DEFAULT"
      self.cmd = cmd
      self.keepalive = keepalive
      self.peers = list()
      self.peersSTDERR = list()
      
      self.alive = False
      self.mInput = False
      self.ibuff = ""
      self.obuff = ""

      self.alive = False
      self.mInput = False

   def getPeersSTDERR(self):

      return self.peersSTDERR

   def setPeersSTDERR(self,pstderr):

      self.peersSTDERR = pstderr

   def getCmd(self):

      return self.cmd

   def setCmd(self,cmd):

      self.cmd = cmd

   def setKeepalive(self,async):

      self.async = keepalive

   def getKeepalive(self):

      return self.keepalive


   def onTextChange(self,widget):
      print "ONTEXTCHANGE:", widget

      if (widget == synappGTK.iname):
         self.name = synappGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(synappGTK.iname.get_text())

      elif (widget == synappGTK.icmd):
         self.cmd = synappGTK.icmd.get_text()

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
         synappGTK.icmd.disconnect(synappGTK.chdict['icmd'])
         synappGTK.icolorBtn.disconnect(synappGTK.chdict['icolorBtn'])

   def getPropWidget(self):

      synappGTK.iname.set_text(self.name)
      synappGTK.icmd.set_text(self.cmd)
      synappGTK.icolor.set_text(self.color)
      

      synappGTK.chdict['iname'] = synappGTK.iname.connect("changed",self.onTextChange)
      synappGTK.chdict['icmd'] = synappGTK.icmd.connect("changed",self.onTextChange)
      synappGTK.chdict['icolorBtn'] = synappGTK.icolorBtn.connect("clicked",self.onColorChange)

      return synappGTK.o



class synserv(synobj):

   nbinst = 0


   def sockConnect(self):

      (host,port) = self.connectInfos.split(":")

      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      try:
         sockfd.connect((host,int(port)))
      except: 
         print "ERROR: CANT CONNECT TO %s:%s" % (host,port)
         return -1

      fcntl(sockfd,F_SETFL,fcntl(sockfd,F_GETFL) | os.O_NONBLOCK)
      
      return sockfd

      #s.send('Hello, world')
      #data = s.recv(1024)
      #s.close()
   
   def run(self):
          
      self.alive = True
      sockfd = self.sockConnect()

      while(self.alive == True and (self.autoreco or sockfd != -1) ):

         while(sockfd == -1 and self.autoreco and self.alive):
            print "RECONNECTING"
            sockfd = self.sockConnect()

         (rr,wr,er) = select.select([sockfd],[],[],2)
         for fd in rr:    
            line = fd.recv(4096)
            if (line != ""):
               self.obuff = line
               self.broadcast() 
      
         if (self.ibuff != "" ):
            (input_num,sep,content) = self.ibuff.partition(":")
            sockfd.send(content)
         

   def __init__(self,name,proto="Tcp",connectInfos="",keepalive=True):

      synserv.nbinst+=1

      self.name = name
      self.color="DEFAULT"
      self.connectInfos = connectInfos
      self.keepalive = keepalive
      self.autoreco = True
      self.proto = proto

      self.peers = list()
      
      self.ibuff = ""
      self.obuff = ""

      self.alive = False
      self.mInput = False

      

  
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
        synservGTK.icolor.set_text(self.color)

        IMVEC.activeDoc.getActiveM().getSynItem().getMF().set_property("fill_color",self.color)
        IMVEC.activeDoc.getActiveM().getSynItem().getLtext().set_property("fill_color",self.color)

        
        colorseldlg.destroy()
      elif response == gtk.RESPONSE_CANCEL:
        colorseldlg.destroy()


   def onTextChange(self,widget):
      print "ONTEXTCHANGE:", widget

      if (widget == synservGTK.iname):
         self.name = synservGTK.iname.get_text()
         IMVEC.activeDoc.getActiveM().getSynItem().setText(synservGTK.iname.get_text())

      elif (widget == synservGTK.ici):
         self.connectInfos = synservGTK.ici.get_text()

      elif (widget == synservGTK.iproto):

         self.proto = widget.get_active_text()
 

      elif (widget == synservGTK.iar):
         if widget.get_active_text() == "True":
            self.autoreco = True 
        
         if widget.get_active_text() == "False":
            self.autoreco = False


   def disconnectAll(self):

         synservGTK.iname.disconnect(synservGTK.chdict['iname'])
         synservGTK.icolorBtn.disconnect(synservGTK.chdict['icolorBtn'])
         synservGTK.ici.disconnect(synservGTK.chdict['ici'])
         synservGTK.iproto.disconnect(synservGTK.chdict['iproto'])      
         synservGTK.iar.disconnect(synservGTK.chdict['iar']) 


   def getPropWidget(self):

      synservGTK.iname.set_text(self.name)
      synservGTK.icolor.set_text(self.color)
      synservGTK.ici.set_text(self.connectInfos)


      if (self.proto == "Tcp"): 

         synservGTK.iproto.set_active(0)
      else:
         synservGTK.iproto.set_active(1)


      if (self.autoreco): 

         synservGTK.iar.set_active(0)
      else:
         synservGTK.iar.set_active(1)







      synservGTK.chdict['iname'] = synservGTK.iname.connect("changed",self.onTextChange)
      synservGTK.chdict['icolorBtn'] = synservGTK.icolorBtn.connect("clicked",self.onColorChange)
      synservGTK.chdict['ici'] = synservGTK.ici.connect("changed",self.onTextChange)
      synservGTK.chdict['iproto'] = synservGTK.iproto.connect("changed",self.onTextChange)      
      synservGTK.chdict['iar'] = synservGTK.iar.connect("changed",self.onTextChange) 


      return synservGTK.o
