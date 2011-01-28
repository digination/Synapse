from synapseIMVEC import *
from copy import *

class synapseHistory:

   history = None

   def addHistory(self):

      try:
         savepath = IMVEC.unsavedDocs[IMVEC.activeDoc.getId()]
      except:
         IMVEC.unsavedDocs[IMVEC.activeDoc.getId()] = "foo"
         IMVEC.activeDoc.setHeadLabel("*%s" % (IMVEC.activeDoc.getHeadLabelText() ))
  


      try:      
         curdoc_name = IMVEC.activeDoc.getName()
      except:
         return True

      try:
         len_curdoc_history = len(self.undodict[curdoc_name])
      except:
         self.undodict[curdoc_name] = list()
         len_curdoc_history = 0

      IMVEC.dbg.debug("APPENDING NEW VERSION IN HISTORY",tuple(),dbg.SEXDEBUG)
      self.append(IMVEC.activeDoc)
      

   def append(self,document):

   
      if len(self.undodict[document.getName()]) > self.length:
         self.undodict[document.getName()].pop(0)      
      self.undodict[document.getName()].append(document.serializeAll())
   

   def appendR(self,document):

      if len(self.redodict[document.getName()]) > self.length:
         self.redodict[document.getName()].pop(0)      
      self.redodict[document.getName()].append(document.serializeAll())


   def __init__(self,history_length):

      self.length = history_length
      self.undodict = dict()
      self.redodict = dict()


   def undo(self):

      IMVEC.dbg.debug("UNDO LAST CHANGE",tuple(),dbg.SEXDEBUG)

      try:
         self.appendR(IMVEC.activeDoc)
      except:
         self.redodict[IMVEC.activeDoc.getName()] = list()
         self.appendR(IMVEC.activeDoc)

      serialdoc_to_use = self.undodict[IMVEC.activeDoc.getName()].pop()
      IMVEC.activeDoc.deserializeAll(serialdoc_to_use)

   def redo(self):

      IMVEC.dbg.debug("REDO LAST CHANGE",tuple(),dbg.SEXDEBUG)
      print self.redodict[IMVEC.activeDoc.getName()]

      serialdoc_to_use = self.redodict[IMVEC.activeDoc.getName()].pop()
      IMVEC.activeDoc.deserializeAll(serialdoc_to_use)   


   
   



