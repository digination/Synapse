import pygtk
pygtk.require("2.0")
import gtk
import os
import sys
sys.path.append("/usr/lib/synapse")

RES_PATH = "/usr/share/synapse"



class helper(object):



   def __init__(self):

      builder = gtk.Builder()
      builder.add_from_file("%s/ui/helper.xml" % (RES_PATH))
    
   
      self.window = builder.get_object("window1")
      self.cancel_btn = builder.get_object("cancel_btn")
      self.ok_btn = builder.get_object("ok_btn")
      self.exprTV = builder.get_object("expr")
      self.descrLbl =  builder.get_object("descr")

      self.enclosure = builder.get_object("enclosure")
      self.window.show()
      self.setEnclosureContent()



class scapyHelper(helper):



   def __init__(self):

      helper.__init__(self)


   def setEnclosureContent(self):

      o = gtk.HBox()


      vbox1 = gtk.VBox()
      vbox2 = gtk.VBox()
     
      vbox1.show()
      vbox2.show()


      lfct = gtk.Label("Add function:")
      lfct.show()

      self.fct = gtk.ComboBox()
      self.fct.show()

  
      ls1 = gtk.ListStore(str)
      self.fct.set_model(ls1)
      cellr1 = gtk.CellRendererText()
      self.fct.pack_start(cellr1)
      self.fct.add_attribute(cellr1, 'text', 0)

      self.fct.append_text("Send Packets (simple)")
      self.fct.append_text("Send Packets (advenced)")
      self.fct.append_text("Sniff")
      self.fct.append_text("Hexdump")
      self.fct.append_text("Traceroute")
      self.fct.append_text("Dump Graphic (image)")
      self.fct.append_text("Dump Graphic (pdf/ps)")
      
      self.fct.set_active(0)

      
      vbox1.pack_start(lfct,False,True,10)
      vbox2.pack_start(self.fct,False,True,10)

      self.enclosure.pack_start(vbox1,False,True,10)
      self.enclosure.pack_start(vbox2,False,True,10)




      return


   

     

  
