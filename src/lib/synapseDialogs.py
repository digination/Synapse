import pygtk
import gtk
import os
import sys
import time

from synapseIMVEC import *




class inputDialog(object):


   def setCallBack(self,callback_ref):
  
      self.ok_btn.connect("clicked",callback_ref)
      self.input.connect("activate",callback_ref)      

   def on_cancel(self,widget):
 
      self.window.destroy()


   def getInput(self):

      return self.input.get_text()

   def getWindow(self):

      return self.window   

   def __init__(self,title):

      builder = gtk.Builder()
      builder.add_from_file("%s/ui/input.xml" % (IMVEC.RES_PATH))
      self.window = builder.get_object("window1")

      self.window.set_title(title)

      self.input = builder.get_object("entry1")
      self.ok_btn = builder.get_object("ok_btn")
      self.cancel_btn = builder.get_object("cancel_btn")
      self.cancel_btn.connect("clicked",self.on_cancel)

     
   def run(self):

      self.window.show()



