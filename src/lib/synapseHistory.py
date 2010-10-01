from synapseIMVEC import *
from copy import *

class synapseHistory:

   history = None

   def addHistory(self):

      try:      
         curdoc_name = IMVEC.activeDoc.getName()
      except:
         return True

      try:
         len_curdoc_history = len(self.undodict[curdoc_name])
      except:
         self.undodict[curdoc_name] = list()
         len_curdoc_history = 0

      print "appending new doc version to history"
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

      try:
         self.appendR(IMVEC.activeDoc)
      except:
         self.redodict[IMVEC.activeDoc.getName()] = list()
         self.appendR(IMVEC.activeDoc)

      serialdoc_to_use = self.undodict[IMVEC.activeDoc.getName()].pop()
      IMVEC.activeDoc.deserializeAll(serialdoc_to_use)

   def redo(self):

      print "REDO"
      print self.redodict[IMVEC.activeDoc.getName()]

      serialdoc_to_use = self.redodict[IMVEC.activeDoc.getName()].pop()
      IMVEC.activeDoc.deserializeAll(serialdoc_to_use)   


   
   



