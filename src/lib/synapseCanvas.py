import goocanvas

import sys
sys.path.append("/usr/lib/synapse")
from synapseObjects import *
from synapseIMVEC import *

import gtk

MAKE_LINE=0

NLPARAMETERS = list()

IMVEC.linkList = list()


MOVED_OBJECT=None
ACTIVE_OBJECT=None
RESIZED_OBJECT = None
COORDS_OFFSET = list()

COORDS = list()
MOUSE_COORDS = list()

ITEM_LIST= list()


def motion_notify(widget, event):
    
      global MOUSE_COORDS
      global MOVED_OBJECT
      global RESIZED_OBJECT
      global COORDS_OFFSET


      MOUSE_COORDS = [int(event.x),int(event.y)]
      
      if RESIZED_OBJECT != None:
         RESIZED_OBJECT.getO().set_property("width",int(event.x) +40 - RESIZED_OBJECT.getO().get_property("x") )
         RESIZED_OBJECT.getO().set_property("height",int(event.y)+40 - RESIZED_OBJECT.getO().get_property("y") )
         RESIZED_OBJECT.getMF().set_property("height",int(event.y) - RESIZED_OBJECT.getO().get_property("y") )
         RESIZED_OBJECT.getMF().set_property("width",int(event.x) - RESIZED_OBJECT.getO().get_property("x") )
         RESIZED_OBJECT.getExtender().set_property("x",RESIZED_OBJECT.getMF().get_property("width")-10)
         RESIZED_OBJECT.getExtender().set_property("y",RESIZED_OBJECT.getMF().get_property("height")-10)

         if str(RESIZED_OBJECT.__class__) == "synapseCanvas.monitorItem":
            RESIZED_OBJECT.updateInputs()
            RESIZED_OBJECT.getWinBorder().set_property("width", RESIZED_OBJECT.getMF().get_property("width")  )
             
            (hidebtn,maxbtn) = RESIZED_OBJECT.getButtons()
            hidebtn.set_property("x", RESIZED_OBJECT.getMF().get_property("width") -40 )
            maxbtn.set_property("x",  RESIZED_OBJECT.getMF().get_property("width") -20 )

         elif str(RESIZED_OBJECT.__class__) == "synapseCanvas.containerItem":
            RESIZED_OBJECT.replaceIcon()




      elif MOVED_OBJECT != None:


         print IMVEC.activeDoc.getItemsAt(int(event.x),int(event.y))

         MOVED_OBJECT.set_property("x",int(event.x)-COORDS_OFFSET[0])
         MOVED_OBJECT.set_property("y",int(event.y)-COORDS_OFFSET[1])

         for link in IMVEC.linkList:
            link.update()


def compute_bary(item):

   coords = tuple()

   item_width = item.get_property("width")

   item_height = item.get_property("height")

   item_x = item.get_parent().get_property("x") +  item.get_property("x")

   item_y = item.get_parent().get_property("y") +  item.get_property("y")

   x = item_x + ( item_width / 2 )

   y = item_y + (item_height / 2 )

   coords = (x,y)

   return coords


def compute_bary_internal(item):

   coords = tuple()

   item_width = item.get_property("width")

   item_height = item.get_property("height")

   item_x = item.get_property("x")

   item_y = item.get_property("y")

   x = item_x + ( item_width / 2 )

   y = item_y + (item_height / 2 )

   coords = (x,y)

   return coords





class synItem():


   def objectSelectionChange(self,item, target_item, event):


      global ACTIVE_OBJECT

      ## Attention ici, probleme de timing
      #ACTIVE_OBJECT.synapp.disconnectAll()

      for child in IMVEC.oprop.get_nth_page(0).get_children():
         IMVEC.oprop.get_nth_page(0).remove(child)
      IMVEC.oprop.get_nth_page(0).add(IMVEC.activeDoc.getContainer().getSynObj(self).getPropWidget())

   def on_mf_released(self,item,target_item,event):
      global MOVED_OBJECT
      MOVED_OBJECT = None

   def on_mf_clicked(self,item,target_item,event):
      
      IMVEC.activeDoc.setActiveM(IMVEC.activeDoc.getContainer().getMemberFromSynItem(self))
      
      if (IMVEC.activeDoc.getPrevM() != None):
         
         if (str(IMVEC.activeDoc.getPrevM().getSynItem().__class__) != "synapseCanvas.linkItem") : 
            IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#cccccc")
         else:
            if IMVEC.activeDoc.getPrevM().getSynObj().getBidir() == False: 
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","black")
            else:
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#00cbff")

         IMVEC.activeDoc.getPrevM().getSynObj().disconnectAll()

      global MOVED_OBJECT
      global COORDS_OFFSET
      global MOUSE_COORDS
      global ACTIVE_OBJECT
      self.mf.set_property("stroke_color","#00ff00")


      if (item != None):
         MOVED_OBJECT = self.getO()
         ACTIVE_OBJECT = self
         COORDS_OFFSET = [ MOUSE_COORDS[0] - self.getO().get_property("x") ,  MOUSE_COORDS[1] - self.getO().get_property("y")]

   #stops link line
   def on_input_clicked(self,item, target_item, event):
      global MAKE_LINE,NLPARAMETERS
      print "INPUT CLICKED", item
      if MAKE_LINE == 1:

         newitem = linkItem(self.root,NLPARAMETERS[0],NLPARAMETERS[1],self,item)
         IMVEC.linkList.append(newitem)
         newobj = synlink("pipe%d" % len(IMVEC.linkList),IMVEC.activeDoc.getContainer().getMemberFromSynItem(NLPARAMETERS[0]).getSynObj(),
                                             IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj())
         
         newobj.setOutputNum(NLPARAMETERS[0].getOutNum(NLPARAMETERS[1]))
         newobj.setInputNum(self.getInNum(item))


         IMVEC.activeDoc.getContainer().append(linker(newobj,newitem))

         IMVEC.activeDoc.getContainer().updatePeers()
         IMVEC.activeDoc.refresh_objects_list()
         
                 
         MAKE_LINE=0
         del NLPARAMETERS[:]
         IMVEC.status_lbl.set_text("")
     
   #starts link line   
   def on_output_clicked(self,item, target_item, event):
      global MAKE_LINE, NLPARAMETERS
      if MAKE_LINE == 0:
         
         NLPARAMETERS.append(self)
         NLPARAMETERS.append(item)
         print "OUTPUT CLICKED", item
         IMVEC.status_lbl.set_text("Choose input object to link with %s" % (IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj().getName()))
         MAKE_LINE = 1


   def getMF(self):
      return self.mf

   def getO(self):

      return self.o
         
   def setText(self,text):

      self.ltext.set_property("text",text)

   def getLtext(self):
  
      return self.ltext


   def connectAll(self):

      self.mf.connect("button-press-event",self.on_mf_clicked)
      self.mf.connect("button-press-event",self.objectSelectionChange)
      self.mf.connect("button-release-event",self.on_mf_released)
      
      if self.icon != None:

         self.icon.connect("button-press-event",self.on_mf_clicked)
         self.icon.connect("button-press-event",self.objectSelectionChange)
         self.icon.connect("button-release-event",self.on_mf_released)

      for inp in self.inputs:
         inp.connect("button-press-event",self.on_input_clicked)

      for out in self.outputs:
         out.connect("button-press-event",self.on_output_clicked)



   def getInput(self,n):

       return self.inputs[n]

   def getOutput(self,n):

      return self.outputs[n]


   def getOutNum(self,output):

      for i in range(0,len(self.outputs)):
         if output == self.outputs[i]:
            return i
            break
      print "ERROR: Output not found"


   def getInNum(self,inp):

      for i in range(0,len(self.inputs)):
         if inp == self.inputs[i]:
            return i
            break
      print "ERROR: Input not found"


class synappItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,radius_x=10,radius_y=10, width=134, height=50,
				stroke_color="#cccccc", fill_color="#152233",tooltip="Application",
				line_width=4)

      self.pixbuf = IMVEC.appPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=52,y=10,pixbuf=self.pixbuf)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",-1)
      self.inputs[0].set_property("y",10)

      
      

      #self.inputs[0].set_property("fill-color-rgba",0x00cbffaa)
      #self.inputs[0].set_property("tooltip","Application's stdin")


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",134)
      self.outputs[0].set_property("y",10)




      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#ff3200", line_width=1))

      self.outputs[1].set_property("x",134)
      self.outputs[1].set_property("y",25)


      
      self.ltext = goocanvas.Text(parent = self.o,font="Sans 8", text="", x=5, y=-16,
						width=100,
						fill_color="#152233")
   
      self.connectAll()





class servItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0, radius_x=10,radius_y=10,width=134, height=50,
				stroke_color="#cccccc", fill_color="#ff9932",
				line_width=4)


      self.pixbuf = IMVEC.servPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=52,y=10,pixbuf=self.pixbuf)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",-1)
      self.inputs[0].set_property("y",10)


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",134)
      self.outputs[0].set_property("y",10)

      
      self.ltext = goocanvas.Text(parent = self.o,font="Sans 8", text="", x=5, y=-16,
						width=100,
						fill_color="#ff9932")
   
      self.connectAll()




class filterItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0, width=80, height=50,
				stroke_color="#cccccc", fill_color="#42215d",
				line_width=4,radius_x=10,radius_y=10)


      self.pixbuf = IMVEC.filterPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=25,y=10,pixbuf=self.pixbuf)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",-1)
      self.inputs[0].set_property("y",10)


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",80)
      self.outputs[0].set_property("y",17)

      
      self.ltext = goocanvas.Text(parent = self.o, text="", x=3, y=-15,
						width=100,
						fill_color="#42215d",font="sans 8")
   
      self.connectAll()








class timerItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,radius_x=10,radius_y=10, width=50, height=50,
				stroke_color="#cccccc", fill_color="#cc99ff",
				line_width=4)

      self.pixbuf = IMVEC.timerPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=10,y=10,pixbuf=self.pixbuf)

    

      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",0)
      self.inputs[0].set_property("y",10)



      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",51)
      self.outputs[0].set_property("y",10)
      
      self.ltext = goocanvas.Text(parent = self.o, text="", x=3, y=-15,
						width=100,font="sans 8", fill_color="#cc99ff")

      self.connectAll()
      


class injectorItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.mf = goocanvas.Path(parent = self.o, data="M 10 10 L 60 50 L 10 90 L 10 10 z", stroke_color="#cccccc", fill_color="#cc99ff", line_width=4)

      self.pixbuf = IMVEC.injectorPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=13,y=33,pixbuf=self.pixbuf)


      self.outputs.append(goocanvas.Rect( parent = self.o,x=60, y=45, width=10, height=10,
				stroke_color="black", fill_color="#00cbff",
				line_width=1))
      
      self.ltext = goocanvas.Text(parent = self.o, text="",font="sans 8", x=7, y=-7,
						width=100,fill_color="#cc99ff")

      self.connectAll()
     

class testItem(synItem):

   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0, width=50, height=50,
				stroke_color="#cccccc", fill_color="#333333",
				line_width=4)

      self.mf.set_simple_transform(0,0,1,45)

      self.pixbuf = IMVEC.testPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=-15,y=18,pixbuf=self.pixbuf)


      self.inputs.append(goocanvas.Rect( parent = self.o,x=-40, y=30, width=10, height=10,
				stroke_color="black", fill_color="#00cbff",
				line_width=1))


      self.outputs.append(goocanvas.Rect( parent = self.o,x=-6, y=67, width=10, height=10,
				stroke_color="black", fill_color="#00cbff",
				line_width=1))
      

      self.outputs.append(goocanvas.Ellipse(parent=self.o,
                            center_x=40,
                            center_y=35,
                            radius_x=6,
                            radius_y=6,
                            stroke_color="black",
                            fill_color="#ff3200",
                            line_width=1.0)
)
     
      self.ltext = goocanvas.Text(parent = self.o, text="", x=-13, y=-16, width=100,fill_color="#333333",font="sans 8")


      self.connectAll()


class muxItem(synItem):

   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0, width=50, height=134,
				stroke_color="#cccccc", fill_color="#028ba3",
				line_width=4,radius_x=10,radius_y=10)

      
      self.icon = goocanvas.Image(parent = self.o,x=10,y=5,pixbuf=IMVEC.muxPixbuf)
      #self.icon = None
      

      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",0)
      self.inputs[0].set_property("y",10)

      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[1].set_property("x",0)
      self.inputs[1].set_property("y",31)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[2].set_property("x",0)
      self.inputs[2].set_property("y",52)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[3].set_property("x",0)
      self.inputs[3].set_property("y",73)

      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[4].set_property("x",0)
      self.inputs[4].set_property("y",94)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[5].set_property("x",0)
      self.inputs[5].set_property("y",115)
     


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 23 L 0 45 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",51)
      self.outputs[0].set_property("y",45)



      self.ltext = goocanvas.Text(parent = self.o,font="Sans 8", text="", x=5, y=-16,
						width=100,
						fill_color="#028ba3")

      self.connectAll()


class demuxItem(synItem):

   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0, width=50, height=134,
				stroke_color="#cccccc", fill_color="#660033",
				line_width=4,radius_x=10,radius_y=10)

      self.pixbuf = IMVEC.demuxPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=7,y=10,pixbuf=self.pixbuf)



      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",50)
      self.outputs[0].set_property("y",10)

      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[1].set_property("x",50)
      self.outputs[1].set_property("y",31)


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[2].set_property("x",50)
      self.outputs[2].set_property("y",52)


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[3].set_property("x",50)
      self.outputs[3].set_property("y",73)

      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[4].set_property("x",50)
      self.outputs[4].set_property("y",94)


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[5].set_property("x",50)
      self.outputs[5].set_property("y",115)


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 23 L 0 45 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",0)
      self.inputs[0].set_property("y",45)



      self.ltext = goocanvas.Text(parent = self.o,font="Sans 8", text="", x=5, y=-16,
						width=100,
						fill_color="#660033")
      self.connectAll()




class linkItem():


   def objectSelectionChange(self,item, target_item, event):

      for child in IMVEC.oprop.get_nth_page(0).get_children():
         IMVEC.oprop.get_nth_page(0).remove(child)
      IMVEC.oprop.get_nth_page(0).add(IMVEC.activeDoc.getContainer().getSynObj(self).getPropWidget())


   def on_mf_clicked(self,item,target_item,event):

      self.on_line_clicked(item,target_item,event)


   def on_line_clicked(self,item,target_item,event):

      IMVEC.activeDoc.setActiveM(IMVEC.activeDoc.getContainer().getMemberFromSynItem(self))
      
      if (IMVEC.activeDoc.getPrevM() != None):
         if (str(IMVEC.activeDoc.getPrevM().getSynItem().__class__) != "synapseCanvas.linkItem") : 
            IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#cccccc")
         else:
            if IMVEC.activeDoc.getPrevM().getSynObj().getBidir() == False: 
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","black")
            else:
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#00cbff")

         IMVEC.activeDoc.getPrevM().getSynObj().disconnectAll()

      self.line.set_property("stroke-color","#00ff00")
      
      

   def getMF(self):
      return self.line


   def getO(self):
      return self.line

   def update(self):
      new_coords = tuple()
      new_coords = compute_bary(self.outp) + compute_bary(self.inp)
     
      self.line.set_property("data","M %d %d L %d %d" % new_coords )


   def __init__(self,parent_canvas,outItem,outp,inItem,inp):

     self.root = parent_canvas
     self.inItem = inItem
     self.outItem = outItem
     self.outp = outp
     self.inp = inp
     
     coords = tuple()
     coords = compute_bary(outp) + compute_bary(inp)        

     self.line = goocanvas.Path(parent=self.root,data="M %d %d L %d %d" % coords, stroke_color="black")  

     self.line.connect("button-press-event",self.on_line_clicked)
     self.line.connect("button-press-event",self.objectSelectionChange)


class monitorItem(synItem):

   def flush(self):
      self.ltext.set_property("text","")

   def on_extend_click(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = self


   def on_hide_click(self,item,target_item,event):
      if self.mf.get_property("height") > 16:
         self.mf.set_property("height",16)

         #self.extender.set_property("x",self.mf.get_property("width")-10)
         #self.extender.set_property("y",self.mf.get_property("height")-10)
         self.extender.set_property("fill_color_rgba",0xcccccc00)


      else:
         self.mf.set_property("height",200)

         self.extender.set_property("x",self.mf.get_property("width")-10)
         self.extender.set_property("y",self.mf.get_property("height")-10)
         self.extender.set_property("fill_color_rgba",0xccccccff)

         


   def on_maximize_click(self,item,target_item,event):


      if self.mf.get_property("height") != self.root.get_property("height"):
   
         self.o.set_property("x",0)
         self.o.set_property("y",0)
         self.mf.set_property("height",self.root.get_property("height"))
         self.mf.set_property("width",self.root.get_property("width"))
         self.winborder.set_property("width",self.root.get_property("width"))

         self.updateInputs()
            
         self.hideBtn.set_property("x", self.mf.get_property("width") -40 )
         self.maxBtn.set_property("x",  self.mf.get_property("width") -20 )
         self.extender.set_property("x",self.mf.get_property("width")-10)
         self.extender.set_property("y",self.mf.get_property("height")-10)
         




   def on_extend_release(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = None


   def on_extend_enter(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.extendCursor)


   def on_extend_leave(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(None)


   def updateInputs(self):

      print "MF_X_COORD:", self.mf.get_property("x")

      #self.inputs[0].set_property("y",(self.mf.get_property("height")-30)/2 )
      #self.inputs[0].set_property("x",self.mf.get_property("x")-1)
       
      #self.inputs[1].set_property("y",(self.mf.get_property("height")-30)/2 )
      #self.inputs[1].set_property("x",self.mf.get_property("width")-4)
      #self.inputs[2].set_property("x",(self.mf.get_property("width")-30)/2 )
      #self.inputs[2].set_property("x",(self.mf.get_property("width")-30)/2 )
      #self.inputs[2].set_property("y",self.mf.get_property("height")-4)
   
      for link in IMVEC.linkList:
         link.update()


   def getExtender(self):
      return self.extender

   def getWinBorder(self):
      return self.winborder

   def getButtons(self):
      return (self.hideBtn,self.maxBtn)


   def setComment(self,text):

      self.ltext.set_property("text",text)



   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.inputs = list()
      self.outputs = list()

     
      
      self.mf = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=0, radius_y=0,width=300, height=200,
				stroke_color="#cccccc", fill_color_rgba=0x000000da,
				line_width=0)


      #Previous border color: 0x30303090
      self.winborder = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=0, radius_y=0,width=300, height=16,
				stroke_color="#ffffff", fill_color_rgba=0xddddddff,
				line_width=0) 



      self.hideBtn = goocanvas.Image(parent = self.o,x=260,y=5,pixbuf=IMVEC.monitorHidePixbuf)
      self.maxBtn = goocanvas.Image(parent = self.o,x=280,y=5,pixbuf=IMVEC.monitorMaximizePixbuf) 



      print "MF_X_COORD:", self.mf.get_property("x")


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 8 L 0 16 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=0))

      self.inputs[0].set_property("x",5)
      self.inputs[0].set_property("y",5)

      #self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 15 L 10 0 L 10 30 L 0 15 z",
                                      #stroke_color="black", fill_color="#00cbff", line_width=1))

      #self.inputs[1].set_property("x",196)
      #self.inputs[1].set_property("y",40)


      #self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 30 0 L 15 10 L 0 0 z",
                                      #stroke_color="black", fill_color="#00cbff", line_width=1))

      #self.inputs[2].set_property("x",90)
      #self.inputs[2].set_property("y",4)


      
      #self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 10 L 15 0 L 30 10 L 0 10 z",
                                      #stroke_color="black", fill_color="#00cbff", line_width=1))

      #self.inputs[2].set_property("x",90)
      #self.inputs[2].set_property("y",96)




      self.ltext = goocanvas.Text(parent = self.o, font="Sans 8" , text="", x=12, y=20,
						width=300,
						fill_color="white")

      self.ltext.set_property("width",300)



      self.icon = None

      self.extender = goocanvas.Path(parent = self.o, data="M 290 205 L 305 190 L 305 205 L 290 205 z", stroke_color="black", fill_color="#cccccc", line_width=0)

     

      self.connectAll()
      self.ltext.connect("button-press-event",self.on_mf_clicked)
      self.ltext.connect("button-press-event",self.objectSelectionChange)
      self.ltext.connect("button-release-event",self.on_mf_released)

      self.winborder.connect("button-press-event",self.on_mf_clicked)
      self.winborder.connect("button-press-event",self.objectSelectionChange)
      self.winborder.connect("button-release-event",self.on_mf_released)

 
      self.extender.connect("button-press-event",self.on_extend_click)
      self.extender.connect("button-release-event",self.on_extend_release)


      self.extender.connect("enter-notify-event",self.on_extend_enter)
      self.extender.connect("leave-notify-event",self.on_extend_leave)      


      self.hideBtn.connect("button-press-event",self.on_hide_click)
      self.maxBtn.connect("button-press-event",self.on_maximize_click)

      



class headerItem():


   def redim(self):

     self.mf.set_property("width",self.root.get_property("width"))

     self.sepLine1.set_property("data","M 0 0 L %d 0" % (self.root.get_property("width")))
     self.sepLine2.set_property("data","M 0 0 L %d 0" % (self.root.get_property("width")))

     if self.h_extended:
        self.sepLine1.set_property("y",25)
        self.sepLine2.set_property("y",65)

      
   def objectSelectionChange(self,item, target_item, event):

      for child in IMVEC.oprop.get_nth_page(0).get_children():
         IMVEC.oprop.get_nth_page(0).remove(child)
      IMVEC.oprop.get_nth_page(0).add(IMVEC.activeDoc.getHeader().getSynObj().getPropWidget())


   def on_mf_clicked(self,item,target_item,event):
      
      IMVEC.activeDoc.setActiveM(IMVEC.activeDoc.getHeader())
      
      if (IMVEC.activeDoc.getPrevM() != None):
         
         if (str(IMVEC.activeDoc.getPrevM().getSynItem().__class__) != "synapseCanvas.linkItem") : 
            IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#cccccc")
         else:
            if IMVEC.activeDoc.getPrevM().getSynObj().getBidir() == False: 
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","black")
            else:
               IMVEC.activeDoc.getPrevM().getSynItem().getMF().set_property("stroke_color","#00cbff")

         IMVEC.activeDoc.getPrevM().getSynObj().disconnectAll()




   def on_showbtn_clicked(self,item,target_item,event):

      if self.mf.get_property("height") == 120:

         self.h_extended = False

         self.sepLine1.set_property("y",-25)
         self.sepLine2.set_property("y",-65)
         self.mf.set_property("height",2)
         self.showbtn.set_property("y",-118)
         self.arrow.set_property("data","M 0 0 L 20 0 L 10 8 L 0 0 z")
         self.arrow.set_property("x",5)
         self.arrow.set_property("y",122)

         self.titleLabel.set_property('fill_color_rgba',0xffffff00)
         self.authorLabel.set_property('fill_color_rgba',0xffffff00)
         self.dateLabel.set_property('fill_color_rgba',0xffffff00)
         self.descrLabel.set_property('fill_color_rgba',0xffffff00)

         #lower the whole canvas of 118px
         if IMVEC.activeDoc != None:
            for item in IMVEC.activeDoc.getContainer().getSynItems():
               print item
               item.getO().set_property("y",item.getO().get_property("y")-118)
          

      else:

         self.h_extended = True

         self.mf.set_property("height",120)
         self.showbtn.set_property("y",0)
         self.sepLine1.set_property("y",25)
         self.sepLine2.set_property("y",65)
         self.arrow.set_property("data","M 0 8 L 10 0 L 20 8 L 0 8 z")
         
         self.arrow.set_property("x",5)
         self.arrow.set_property("y",122)

         self.titleLabel.set_property('fill_color_rgba',0xffffffff)
         self.authorLabel.set_property('fill_color_rgba',0xffffffff)
         self.dateLabel.set_property('fill_color_rgba',0xffffffff)
         self.descrLabel.set_property('fill_color_rgba',0xffffffff)


         #lower the whole canvas of 118px
         if IMVEC.activeDoc != None:
            for item in IMVEC.activeDoc.getContainer().getSynItems():
               print item
               item.getO().set_property("y",item.getO().get_property("y")+118)




   def getMF(self):

      return self.mf


   def resize(self):
      return None

   def hide(self):
      return None
   
   def show(self):
      return None

   def setWorkflowTitle(self,title):
      self.titleLabel.set_property("text",title)
   
   def setWorkflowAuthor(self,author):
      self.authorLabel.set_property("text","Author:\t" + author)
   
   def setWorkflowCreationDate(self,date):
      self.dateLabel.set_property("text","Date:\t" + date)

   def setWorkflowDescr(self,descr):
      self.descrLabel.set_property("text",descr)

   def __init__(self,parent_canvas):

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

     
      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,width=self.root.get_property("width"), height=120, stroke_color="#8BA2BD", fill_color_rgba=0x8BA2BDAA,line_width=0)


      self.showbtn = goocanvas.Group(parent=self.root)

      self.showbtnf = goocanvas.Rect(parent = self.showbtn, x=0, y=120,width=30, height=12, stroke_color="#8BA2BD", fill_color_rgba=0x8BA2BDAA,line_width=0)


      self.arrow = goocanvas.Path(parent = self.showbtn,data="M 0 0 L 20 0 L 10 8 L 0 0 z" ,stroke_color="#333333", fill_color_rgba=0xccccccAA,line_width=1)
      self.arrow.set_property("x",5)
      self.arrow.set_property("y",122)

     
      self.titleLabel = goocanvas.Text(parent = self.o, font="Sans 10" , text="Workflow Ittle", x=7, y=3,
						width=200,
						fill_color="white")

      self.titleLabel.set_property("width",self.root.get_property("width"))


      self.sepLine1 = goocanvas.Path(parent = self.o, data="M 0 0 L %d 0" % (self.root.get_property("width")),fill_color="white",line_width=1)


      self.sepLine1.set_property("x",0)
      self.sepLine1.set_property("y",23)



      self.authorLabel = goocanvas.Text(parent = self.o, font="Sans 10" , text="Author:\ttoor", x=7, y=29, fill_color="white")

      self.authorLabel.set_property("width",self.root.get_property("width"))


      self.dateLabel = goocanvas.Text(parent = self.o, font="Sans 10" , text="Date:\t01/01/2010", x=7, y=42,fill_color="white")

      self.dateLabel.set_property("width",self.root.get_property("width"))


      self.sepLine2 = goocanvas.Path(parent = self.o, data="M 0 0 L %d 0" % (self.root.get_property("width")),fill_color="white",line_width=1)

      self.sepLine2.set_property("x",0)
      self.sepLine2.set_property("y",63)


      self.descrLabel = goocanvas.Text(parent = self.o, font="Sans 10" , text="Short Description", x=7, y=68, fill_color="white")


      self.descrLabel.set_property("width",self.root.get_property("width"))



      self.showbtn.connect("button-press-event",self.on_showbtn_clicked)

      self.mf.connect("button-press-event",self.on_mf_clicked)
      self.mf.connect("button-press-event",self.objectSelectionChange)

      self.on_showbtn_clicked(self,None,None)





class commentItem(synItem):


   def on_extend_click(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = self

   def on_extend_release(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = None


   def on_extend_enter(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.extendCursor)


   def on_extend_leave(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(None)



   def getExtender(self):
      return self.extender

   def setComment(self,text):

      self.ltext.set_property("text",text)

   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.inputs = list()
      self.outputs = list()

      self.mf = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=15, radius_y=15,width=200, height=100,
				stroke_color="#cccccc", fill_color_rgba=0x333333aa,
				line_width=0)

      self.ltext = goocanvas.Text(parent = self.o, font="Sans 10" , text="this is a comment box", x=10, y=10,
						width=200,
						fill_color="white")



      self.icon = None


      self.extender = goocanvas.Image(parent = self.o,x=185,y=85,pixbuf=IMVEC.resizePixbuf) 

      #goocanvas.Path(parent = self.o, data="M 185 100 L 200 85 L 200 100 L 185 100 z", stroke_color="black", fill_color="#cc99ff", line_width=1)
      
      self.extender.set_property("x",self.extender.get_property("x")+5)
      self.extender.set_property("y",self.extender.get_property("y")+5)
   
      self.connectAll()
      self.ltext.connect("button-press-event",self.on_mf_clicked)
      self.ltext.connect("button-press-event",self.objectSelectionChange)
      self.ltext.connect("button-release-event",self.on_mf_released)
 

      self.extender.connect("enter-notify-event",self.on_extend_enter)
      self.extender.connect("leave-notify-event",self.on_extend_leave)


      self.extender.connect("button-press-event",self.on_extend_click)      
      self.extender.connect("button-release-event",self.on_extend_release)


    
class containerItem(synItem):


   def replaceIcon(self):

      (mfbary_x,mfbary_y) = compute_bary_internal(self.mf)

      self.icon.set_property("x",mfbary_x-16)
      self.icon.set_property("y",mfbary_y-16)

   def on_extend_click(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = self

   def on_extend_release(self,item,target_item,event):
      global RESIZED_OBJECT
      RESIZED_OBJECT = None



   def on_extend_enter(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.extendCursor)


   def on_extend_leave(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(None)


   def getExtender(self):
      return self.extender

   def setText(self,text):

      self.ltext.set_property("text",text)

   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()


      self.pixbuf = IMVEC.containerPixbuf
      self.exportPixbuf = IMVEC.exportPixbuf
      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.inputs = list()
      self.outputs = list()

     
      self.mf = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=15, radius_y=15,width=300, height=200,
				stroke_color="#000000", fill_color_rgba=0x151515dd,
				line_width=2)


      self.head = goocanvas.Rect(parent = self.o, x=6, y=6,radius_x=15, radius_y=15, width=150, height=35,
				stroke_color="#cccccc", fill_color_rgba=0xcccccccc,
				line_width=0)
      

      self.icon = goocanvas.Image(parent = self.o,x=0,y=0,pixbuf=self.pixbuf)
      self.replaceIcon()
     

     
      self.exporticon = goocanvas.Image(parent = self.o,x=10,y=7,pixbuf=self.exportPixbuf)



      self.ltext = goocanvas.Text(parent = self.o, font="Sans 8" , text="foobar", x=50, y=17,
						width=200,
						fill_color="back")






      self.extender = goocanvas.Image(parent = self.o,x=285,y=185,pixbuf=IMVEC.resizePixbuf) 

      #goocanvas.Path(parent = self.o, data="M 185 100 L 200 85 L 200 100 L 185 100 z", stroke_color="black", fill_color="#cc99ff", line_width=1)
      
      self.extender.set_property("x",self.extender.get_property("x")+6)
      self.extender.set_property("y",self.extender.get_property("y")+6)
   
      self.connectAll()
      self.ltext.connect("button-press-event",self.on_mf_clicked)
      self.ltext.connect("button-press-event",self.objectSelectionChange)
      self.ltext.connect("button-release-event",self.on_mf_released)
 


      self.extender.connect("enter-notify-event",self.on_extend_enter)
      self.extender.connect("leave-notify-event",self.on_extend_leave)

     
      self.extender.connect("button-press-event",self.on_extend_click)
      self.extender.connect("button-release-event",self.on_extend_release)

