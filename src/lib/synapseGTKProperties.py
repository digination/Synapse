import gtk
from synapseIMVEC import *


class synapsepositionGTK:

   #position chooser
   o = gtk.VBox()
   pos_hbox1 = gtk.HBox()
   pos_hbox2 = gtk.HBox()
   pos_hbox3 = gtk.HBox()

   top_label = gtk.Label(str="Inputs/Outputs position                               ")
   
   button_left = gtk.Button()
   button_right = gtk.Button()
   button_top = gtk.Button(label="None")
   button_bottom = gtk.Button(label="None")

   
   image_left = gtk.Image()
   image_left.set_from_pixbuf(IMVEC.ioleft)
   image_left.show()   

   image_right = gtk.Image()
   image_right.set_from_pixbuf(IMVEC.ioleft)
   image_right.show()

   bb_image = gtk.Image()
   bb_image.set_from_pixbuf(IMVEC.bbhoriz)
   bb_image.show()

   
   button_left.add(image_left)
   button_right.add(image_right)
   
   fill_lbl1 = gtk.Label(str="     ")
   fill_lbl1.show()

   fill_lbl2 = gtk.Label(str="                       ")
   fill_lbl2.show()


   fill_lbl3 = gtk.Label(str="     ")
   fill_lbl3.show()

   fill_lbl4 = gtk.Label(str="                       ")
   fill_lbl4.show()


   pos_hbox1.pack_start(fill_lbl1,False,True,10)
   pos_hbox1.pack_start(button_top,True,True,10)
   pos_hbox1.pack_start(fill_lbl2,True,True,10)

   pos_hbox2.pack_start(button_left,False,True,10)
   pos_hbox2.pack_start(bb_image,False,True,10)   
   pos_hbox2.pack_start(button_right,False,True,10)


   pos_hbox3.pack_start(fill_lbl3,False,True,10)
   pos_hbox3.pack_start(button_bottom,True,True,10)
   pos_hbox3.pack_start(fill_lbl4,True,True,10)

   o.pack_start(top_label,False,False,5)
   o.pack_start(pos_hbox1,True,True,5)
   o.pack_start(pos_hbox2,True,True,5)
   o.pack_start(pos_hbox3,True,True,5)


   top_label.show()
   button_left.show()
   button_right.show()
   button_top.show()
   button_bottom.show()

   pos_hbox1.show()
   pos_hbox2.show()
   pos_hbox3.show()

   o.show()




class documentGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()

   
   lwidth = gtk.Label(str="Width (px)")
   lheight = gtk.Label(str="Height (px)")

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   iwidth = gtk.Entry()
   iheight = gtk.Entry()


   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lwidth,False,True,10)
   gtkPVbox1.pack_start(lheight,False,True,10)

   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(iwidth,False,True,5)
   gtkPVbox2.pack_start(iheight,False,True,5)


   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.add(gtkPVbox1)
   o.add(gtkPVbox2)

   for child in o.get_children():
      child.show()

   o.show()

   
class synheaderGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   ltitle = gtk.Label(str="Document Title")
   ititle = gtk.Entry()
   lauthor = gtk.Label(str="Author")
   iauthor = gtk.Entry()
   ldate = gtk.Label(str= "Date")
   idate = gtk.Entry()
   ldescr = gtk.Label(str="Description")
   
   idescrBuffer = gtk.TextBuffer()
   idescr = gtk.TextView(buffer=idescrBuffer)
   idescr.set_size_request(300,200)

  

   gtkPVbox1.pack_start(ltitle,False,True,10)
   gtkPVbox1.pack_start(lauthor,False,True,10)
   gtkPVbox1.pack_start(ldate,False,True,10)
   gtkPVbox1.pack_start(ldescr,False,True,10)


   gtkPVbox2.pack_start(ititle,False,True,5)
   gtkPVbox2.pack_start(iauthor,False,True,5)
   gtkPVbox2.pack_start(idate,False,True,5)
   gtkPVbox2.pack_start(idescr,False,True,5)

   



   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.add(gtkPVbox1)
   o.add(gtkPVbox2)

   for child in o.get_children():
      child.show()

   o.show()







class synappGTK:

   o = gtk.VBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")

   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)


   
   iname = gtk.Entry()
   lcmd = gtk.Label(str="command")
   icmd = gtk.Entry()
   lwoi = gtk.Label(str= "Wake on Input")
   lbo = gtk.Label(str="Buffured Output")   
   lsl = gtk.Label(str="Split Lines")


   iwoi = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   iwoi.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   iwoi.pack_start(cellr0)
   iwoi.add_attribute(cellr0, 'text', 0)

   iwoi.append_text("True")
   iwoi.append_text("False")
   iwoi.set_active(0)

   ibo = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   ibo.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   ibo.pack_start(cellr0)
   ibo.add_attribute(cellr0, 'text', 0)

   ibo.append_text("True")
   ibo.append_text("False")
   ibo.set_active(1)


   isl = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   isl.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   isl.pack_start(cellr0)
   isl.add_attribute(cellr0, 'text', 0)

   isl.append_text("True")
   isl.append_text("False")
   isl.set_active(1)




   #position

   pos_box = synapsepositionGTK.o


   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lcmd,False,True,10)
   gtkPVbox1.pack_start(lwoi,False,True,10)
   gtkPVbox1.pack_start(lbo,False,True,10)
   gtkPVbox1.pack_start(lsl,False,True,10)

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(icmd,False,True,5)
   gtkPVbox2.pack_start(iwoi,False,True,5)
   gtkPVbox2.pack_start(ibo,False,True,5)
   gtkPVbox2.pack_start(isl,False,True,5)

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   gtkPVbox1.show()
   gtkPVbox2.show()

   first_container = gtk.HBox()

   first_container.pack_start(gtkPVbox1,False,True,10)
   first_container.pack_start(gtkPVbox2,False,True,10) 
   first_container.show()


   chdict = dict()


   o.pack_start(first_container,False,True,10)
   o.pack_start(pos_box,False,True,10)

   o.show()





class synservGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   lci = gtk.Label(str="Host:Port")
   ici = gtk.Entry()
   
   lproto = gtk.Label(str="Protocol")
   iproto = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   iproto.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   iproto.pack_start(cellr0)
   iproto.add_attribute(cellr0, 'text', 0)

   iproto.append_text("Tcp")
   iproto.append_text("Udp")
   iproto.set_active(0)

   
   lar = gtk.Label(str="Auto Reconnect")
   iar = gtk.ComboBox()
   ls1 = gtk.ListStore(str)
   iar.set_model(ls1)
   cellr1 = gtk.CellRendererText()
   iar.pack_start(cellr1)
   iar.add_attribute(cellr1, 'text', 0)

   iar.append_text("True")
   iar.append_text("False")
   iar.set_active(0)



   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lci,False,True,10)
   gtkPVbox1.pack_start(lproto,False,True,10)  
   gtkPVbox1.pack_start(lar,False,True,10)  
 
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(ici,False,True,5)
   gtkPVbox2.pack_start(iproto,False,True,5)   
   gtkPVbox2.pack_start(iar,False,True,5)   

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()
  
   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()



class syndemuxGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   ltimeout = gtk.Label(str="timeout(ms)")
   lseparator = gtk.Label(str="Separator")
   iseparator = gtk.Entry()
      
   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lseparator,False,True,10)
  
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(iseparator,False,True,5)

  
   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()


class synmuxGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()
   ltimeout = gtk.Label(str="timeout(ms)")
   itimeout = gtk.Entry()
   ldata = gtk.Label(str="Data")
   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   idataBuffer = gtk.TextBuffer()
   idata = gtk.TextView(buffer=idataBuffer)

   idata.set_size_request(300,200)
   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(ltimeout,False,True,10)
   gtkPVbox1.pack_start(ldata,False,True,10)
  
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(itimeout,False,True,5)
   gtkPVbox2.pack_start(idata,False,True,5)
  

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()





class syntestGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)


   ltt = gtk.Label(str="test type")
   lop = gtk.Label(str="Operand")
   lret = gtk.Label(str="Return")
   
   itt = gtk.ComboBox()
   ls0 = gtk.ListStore(str)
   itt.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   itt.pack_start(cellr0)
   itt.add_attribute(cellr0, 'text', 0)


   itt.append_text("Stream equals")
   itt.append_text("Stream contains")
   itt.append_text("int(Stream) <=")
   itt.append_text("int(Stream) >=")
   itt.append_text("int(Stream) <")
   itt.append_text("int(Stream) >")

   itt.set_active(0)


   iret = gtk.ComboBox()
   ls1 = gtk.ListStore(str)
   iret.set_model(ls1)
   cellr1 = gtk.CellRendererText()
   iret.pack_start(cellr1)
   iret.add_attribute(cellr1, 'text', 0)

   iret.append_text("Stream")
   iret.append_text("Operand")

   iret.set_active(0)
   


   iop = gtk.Entry()


   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(ltt,False,True,10)
   gtkPVbox1.pack_start(lop,False,True,10)
   gtkPVbox1.pack_start(lret,False,True,10)

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(itt,False,True,5)
   gtkPVbox2.pack_start(iop,False,True,5)
   gtkPVbox2.pack_start(iret,False,True,5)


   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():

      child.show()

   o.show()


class syncomGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   ltext = gtk.Label(str="Comment")
   
   colorbox = gtk.HBox()
   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   colorbox.pack_start(icolorBtn,False,True,5)
   colorbox.pack_start(icolor,False,True,5)
   icolor.show()
   icolorBtn.show()
   



   itextBuffer = gtk.TextBuffer()
   itext = gtk.TextView(buffer=itextBuffer)
   
   gtkPVbox1.pack_start(colorbox,False,True,10)
   gtkPVbox1.pack_start(ltext,False,True,10)
   gtkPVbox1.pack_start(itext,True,True,10)

 
   chdict = dict()

   for child1 in gtkPVbox1.get_children():
      child1.show()
     
   o.add(gtkPVbox1)
   
   for child in o.get_children():
      child.show()
   o.show()



class synjectorGTK:


   o = gtk.HBox()
   
  
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)


   lit = gtk.Label(str="Injector Type")
   iit = gtk.ComboBox()


   lstring = gtk.Label(str="String")
   istring = gtk.Entry()
   
   lstringList = gtk.Label(str="String List")
   idataBuffer = gtk.TextBuffer()
   istringList = gtk.TextView(buffer=idataBuffer)
   istringList.set_size_request(300,200)  

   llpm = gtk.Label(str="Lines per message")
   ilpm = gtk.Entry()
   
   
   ls0 = gtk.ListStore(str)
   iit.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   iit.pack_start(cellr0)
   iit.add_attribute(cellr0, 'text', 0)

   iit.append_text("String")
   iit.append_text("String List")
   iit.append_text("File")

   iit.set_active(0)

   lloop = gtk.Label(str="Loop Mode")
   
   iloop = gtk.ComboBox()
   ls1 = gtk.ListStore(str)
   iloop.set_model(ls1)
   cellr1 = gtk.CellRendererText()
   iloop.pack_start(cellr1)
   iloop.add_attribute(cellr1, 'text', 0)

   iloop.append_text("False")
   iloop.append_text("True")
   iloop.set_active(0)

   
   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lit,False,True,10) 
   gtkPVbox1.pack_start(lloop,False,True,10)   
   gtkPVbox1.pack_start(lstring,False,True,10)
   gtkPVbox1.pack_start(lstringList,False,True,10)
   

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(iit,False,True,5)
   gtkPVbox2.pack_start(iloop,False,True,5)
   gtkPVbox2.pack_start(istring,False,True,5)
   gtkPVbox2.pack_start(istringList,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()


   lstring.hide()
   istring.hide()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)


   for child in o.get_children():

      child.show()

   o.show()


class synlinkGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lbidir = gtk.Label(str="Bidirectional")
   ibidir = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   ibidir.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   ibidir.pack_start(cellr0)
   ibidir.add_attribute(cellr0, 'text', 0)

   ibidir.append_text("False")
   ibidir.append_text("True")
   ibidir.set_active(0)


   gtkPVbox1.pack_start(lbidir,False,True,10)
   gtkPVbox2.pack_start(ibidir,False,True,5)
  
   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():

      child.show()

   o.show()



class synfilterGTK:


   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   lft = gtk.Label(str="Filter Type")
   ift = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   ift.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   ift.pack_start(cellr0)
   ift.add_attribute(cellr0, 'text', 0)

   ift.append_text("Simple Grep")
   ift.append_text("PCRE Grep")
   ift.append_text("Sed Expression")
   ift.append_text("Awk Script")  

   ift.set_active(0)

   ldata = gtk.Label(str="Data")
   idataBuffer = gtk.TextBuffer()
   idata = gtk.TextView(buffer=idataBuffer)
   idata.set_size_request(300,200)   
   

   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lft,False,True,10)
   gtkPVbox1.pack_start(ldata,False,True,10)   

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(ift,False,True,5)
   gtkPVbox2.pack_start(idata,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      if (child2 != None):
         child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():

      child.show()

   o.show()


class syntimerGTK:


   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   iname = gtk.Entry()

   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)

   linterval = gtk.Label(str="interval (ms)")
   iinterval = gtk.Entry()
   iinterval.set_text("1000")

   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(linterval,False,True,10)
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(iinterval,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      if (child2 != None):
         child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():

      child.show()

   o.show()


class synmonitorGTK:

   o = gtk.HBox()

   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()

   lwoi = gtk.Label(str= "Wake on Input")
   iwoi = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   iwoi.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   iwoi.pack_start(cellr0)
   iwoi.add_attribute(cellr0, 'text', 0)

   iwoi.append_text("True")
   iwoi.append_text("False")
   iwoi.set_active(0)

   gtkPVbox1.pack_start(lwoi,False,True,10)
   gtkPVbox2.pack_start(iwoi,False,True,5)

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      if (child2 != None):
         child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():

      child.show()

   o.show()



class syncontainerGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")

   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   
   iname = gtk.Entry()

   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
  
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
 
   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()



class synreportGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   #loutput = gtk.Label(str="Output File")
   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   

   #ifile = gtk.HBox()
   ifilename = gtk.Entry()
   ibrowse = gtk.Button(label="Save To ")
   #ifile.pack_start(ifilename,False,True,5)
   #ifile.pack_start(ibrowse,False,True,0)
   ifilename.show()
   ibrowse.show()
   


   iname = gtk.Entry()

   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(ibrowse,False,True,3)  

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(ifilename,False,True,7) 

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()



class synlabelGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   lcrlf = gtk.Label(str="Trailing CRLF")

   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   
   iname = gtk.Entry()


   icrlf = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   icrlf.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   icrlf.pack_start(cellr0)
   icrlf.add_attribute(cellr0, 'text', 0)

   icrlf.append_text("True")
   icrlf.append_text("False")
   icrlf.set_active(0)


   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lcrlf,False,True,10)

  
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(icrlf,False,True,5) 

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()





class synkbdGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")


   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   
   iname = gtk.Entry()


   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
  
   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()




class synpyGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   lpcuni = gtk.Label(str="PCUNI")


   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   
   iname = gtk.Entry()

   ipcuni = gtk.ComboBox()

   ls0 = gtk.ListStore(str)
   ipcuni.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   ipcuni.pack_start(cellr0)
   ipcuni.add_attribute(cellr0, 'text', 0)

   ipcuni.append_text("True")
   ipcuni.append_text("False")
   ipcuni.set_active(0)




   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lpcuni,False,True,10)  


   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(ipcuni,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()


class syndbGTK:

   o = gtk.HBox()
   gtkPVbox1 = gtk.VBox()
   gtkPVbox2 = gtk.VBox()
   lname = gtk.Label(str="Name")
   lconnec = gtk.Label(str="Connector")
   lbtype = gtk.Label(str="Block Type")
   lhostport = gtk.Label(str="Host:port")
   ldb = gtk.Label(str="Database")
   luser = gtk.Label(str="Username")
   lpassword = gtk.Label(str="Password")
   lquery  = gtk.Label(str="Query")

   
   #color definition
   icolor = gtk.Entry()
   icolor.set_state(gtk.STATE_INSENSITIVE)
   icolorBtn = gtk.Button(stock=gtk.STOCK_SELECT_COLOR)
   
   iname = gtk.Entry()

   iconnec = gtk.ComboBox()
  
   ls0 = gtk.ListStore(str)
   iconnec.set_model(ls0)
   cellr0 = gtk.CellRendererText()
   iconnec.pack_start(cellr0)
   iconnec.add_attribute(cellr0, 'text', 0)

   iconnec.append_text("MySQL")
   iconnec.append_text("Postgres")
   iconnec.set_active(0)


   ibtype = gtk.ComboBox()
  
   ls1 = gtk.ListStore(str)
   ibtype.set_model(ls1)
   cellr1 = gtk.CellRendererText()
   ibtype.pack_start(cellr0)
   ibtype.add_attribute(cellr0, 'text', 0)

   ibtype.append_text("No Input")
   ibtype.append_text("Has Input")
   ibtype.set_active(0)

   ihostport = gtk.Entry()
   idb = gtk.Entry()
   iuser = gtk.Entry()
   ipassword = gtk.Entry()

   gtkPVbox1.pack_start(lname,False,True,10)
   gtkPVbox1.pack_start(icolorBtn,False,True,5)
   gtkPVbox1.pack_start(lconnec,False,True,10)  
   gtkPVbox1.pack_start(lbtype,False,True,10)
   gtkPVbox1.pack_start(lhostport,False,True,10) 
   gtkPVbox1.pack_start(ldb,False,True,10)
   gtkPVbox1.pack_start(luser,False,True,10)
   gtkPVbox1.pack_start(lpassword,False,True,10)    

   gtkPVbox2.pack_start(iname,False,True,5)
   gtkPVbox2.pack_start(icolor,False,True,5)
   gtkPVbox2.pack_start(iconnec,False,True,5)
   gtkPVbox2.pack_start(ibtype,False,True,5)
   gtkPVbox2.pack_start(ihostport,False,True,5)
   gtkPVbox2.pack_start(idb,False,True,5)
   gtkPVbox2.pack_start(iuser,False,True,5)
   gtkPVbox2.pack_start(ipassword,False,True,5)

   chdict = dict()

   for child1,child2 in map(None,gtkPVbox1.get_children(),gtkPVbox2.get_children()):
      child1.show()
      child2.show()

   o.pack_start(gtkPVbox1,False,True,10)
   o.pack_start(gtkPVbox2,False,True,0)

   for child in o.get_children():
      child.show()

   o.show()
