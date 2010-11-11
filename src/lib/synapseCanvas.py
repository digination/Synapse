import goocanvas

import sys
sys.path.append("/usr/lib/synapse")
from synapseObjects import *
from synapseIMVEC import *
from synapseUtils import *
from synapseDialogs import inputDialog
from synapseDebug import dbg
from synapseHistory import *

import pygtk
pygtk.require("2.0")
import gtk


MAKE_LINE=0

NLPARAMETERS = list()

IMVEC.linkList = list()


MOVED_OBJECT=None
ACTIVE_OBJECT=None
RESIZED_OBJECT = None
PRE_CONTAINER = None
COORDS_OFFSET = list()

COORDS = list()
MOUSE_COORDS = list()

ITEM_LIST= list()


def motion_notify(widget, event):
    
      global MOUSE_COORDS
      global MOVED_OBJECT
      global RESIZED_OBJECT
      global COORDS_OFFSET
      global PRE_CONTAINER


      MOUSE_COORDS = [int(event.x),int(event.y)]
      IMVEC.mouseCoords = MOUSE_COORDS
      
      try:
         selobject = IMVEC.activeDoc.getSelObject().getSynItem()

         if IMVEC.activeDoc.getSelObject().getSynObj().isEmpty():
            selobject.getMF().set_property("width",int(event.x) - selobject.getMF().get_property("x") )
            selobject.getMF().set_property("height",int(event.y) - selobject.getMF().get_property("y") )
      except:
         pass

      
      if RESIZED_OBJECT != None:

         (abs_coord_x,abs_coord_y) = getAbsoluteCoords(IMVEC.activeDoc.getRootItem(),RESIZED_OBJECT.getO(),0,0)

         ##RESIZE_LIMITATIONS
         try:
            min_dim = RESIZED_OBJECT.getMinDim()
 
            print min_dim

            if (int(event.x) - abs_coord_x < min_dim[0] ):

                #IMVEC.dbg.debug("CONTAINER WIDTH < 240",

                RESIZED_OBJECT.getO().set_property("width",min_dim[0] + 7)
                RESIZED_OBJECT.getMF().set_property("width",min_dim[0])
                RESIZED_OBJECT.getExtender().set_property("x",RESIZED_OBJECT.getMF().get_property("width")-10)
                RESIZED_OBJECT.getExtender().set_property("y",RESIZED_OBJECT.getMF().get_property("height")-10)

                return

            if (int(event.y) - abs_coord_y < min_dim[1] ):

                #print "CONTAINER HEIGHT < %d" % (min_dim[1] + 40 )

                RESIZED_OBJECT.getO().set_property("height",min_dim[1] + 7)
                RESIZED_OBJECT.getMF().set_property("height",min_dim[1])
                RESIZED_OBJECT.getExtender().set_property("x",RESIZED_OBJECT.getMF().get_property("width")-10)
                RESIZED_OBJECT.getExtender().set_property("y",RESIZED_OBJECT.getMF().get_property("height")-10)

                return

         except:
            pass


         RESIZED_OBJECT.getO().set_property("width",int(event.x)+7  - abs_coord_x )
         RESIZED_OBJECT.getO().set_property("height",int(event.y)+7 - abs_coord_y )
         RESIZED_OBJECT.getMF().set_property("height",int(event.y) - abs_coord_y )
         RESIZED_OBJECT.getMF().set_property("width",int(event.x) - abs_coord_x )
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

        
         for syn_c in IMVEC.activeDoc.getSyncontainersList():

            print syn_c.getSynObj().getName()

            sync_width = syn_c.getSynItem().getMF().get_property("width")
            sync_height = syn_c.getSynItem().getMF().get_property("height")
            sync_x = syn_c.getSynItem().getO().get_property("x") -20
            sync_y = syn_c.getSynItem().getO().get_property("y") -20

            if syn_c.getSynItem().getO() != MOVED_OBJECT:
               if (int(event.x)-COORDS_OFFSET[0] < sync_x + sync_width  and int(event.x)-COORDS_OFFSET[0] > sync_x and int(event.y)-COORDS_OFFSET[1] < sync_y + sync_height and int(event.y)-COORDS_OFFSET[1] > sync_y):

        
                  IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.plusCursor)          
                  PRE_CONTAINER = syn_c.getSynItem().getO()
               else:
                  PRE_CONTAINER = None
                  IMVEC.activeDoc.getCanvas().window.set_cursor(None)
               
        



         MOVED_OBJECT.set_property("x",int(event.x)-COORDS_OFFSET[0])
         MOVED_OBJECT.set_property("y",int(event.y)-COORDS_OFFSET[1])

         for link in IMVEC.linkList:
            link.update()


def compute_bary(item):

   coords = tuple()

   item_width = item.get_property("width")

   item_height = item.get_property("height")



   #test if item has transformation matrix:
      
   if (item.get_simple_transform() != None):

      IMVEC.dbg.debug("OBJECT HAS TRANSFORMATION MATRIX",tuple(),dbg.EXDEBUG)

      transform = item.get_simple_transform()

      #change parameters if object is rotated
      if transform[3] == 90:

         buff = item_width
         item_width = item_height * -1
         item_height = buff

      elif transform[3] == 180:

         item_width = item_width * -1
         item_height = item_height * -1

      elif transform[3] == 270: 

         buff = item_width
         item_width = item_height
         item_height = buff * -1



   (nx,ny) = getAbsoluteCoords(IMVEC.activeDoc.getRootItem(),item,0,0)


   #item_x =  +  item.get_property("x")

   #item_y = item.get_parent().get_parent().get_property("y") + item.get_parent().get_property("y") +  item.get_property("y")

   x = nx + ( item_width / 2 )

   y = ny + (item_height / 2 )

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



   def getMinDim(self):

      return (self.min_width,self.min_height)

   def reinit_pos(self):

      for inp in self.inputs:
         inp.set_transform(None)

      for output in self.outputs:
         output.set_transform(None)


   def changeIOPos(self,input_pos,output_pos):

      self.reinit_pos()

      if (input_pos != "left"):

         rotate_coords = compute_bary_internal(self.inputs[0])

         self.inputs[0].rotate(self.tr_table_in[input_pos][2],rotate_coords[0],rotate_coords[1])
         new_coords = IMVEC.activeDoc.getCanvas().convert_to_item_space(self.inputs[0],self.tr_table_in[input_pos][0],self.tr_table_in[input_pos][1])

         self.inputs[0].set_property("x",new_coords[0])
         self.inputs[0].set_property("y",new_coords[1])      


      if (output_pos != "right" and output_pos != None ) :

         process_outputs = 0

         for outp in self.outputs:

            rotate_coords = compute_bary_internal(outp)
            outp.rotate(self.tr_table_out[output_pos][2],rotate_coords[0],rotate_coords[1])


            if (output_pos != "left"):

               new_coords = IMVEC.activeDoc.getCanvas().convert_to_item_space(outp,self.tr_table_out[output_pos][0]+(17*process_outputs),self.tr_table_out[output_pos][1])


            else:

               new_coords = IMVEC.activeDoc.getCanvas().convert_to_item_space(outp,self.tr_table_out[output_pos][0],self.tr_table_out[output_pos][1]+(17*process_outputs))

            outp.set_property("x",new_coords[0])
            outp.set_property("y",new_coords[1])   
            
            process_outputs +=1      






  
   def objectSelectionChange(self,item, target_item, event):

      global ACTIVE_OBJECT

      ## Attention ici, probleme de timing
      #ACTIVE_OBJECT.synapp.disconnectAll()

      for child in IMVEC.oprop.get_nth_page(0).get_children():
         IMVEC.oprop.get_nth_page(0).remove(child)
      IMVEC.oprop.get_nth_page(0).add(IMVEC.activeDoc.getContainer().getSynObj(self).getPropWidget())

   def on_mf_released(self,item,target_item,event):
      global MOVED_OBJECT
      global PRE_CONTAINER

      if PRE_CONTAINER != None and MOVED_OBJECT.get_parent() != PRE_CONTAINER:
         MOVED_OBJECT.set_property("parent",PRE_CONTAINER)
         MOVED_OBJECT.set_property("x",MOVED_OBJECT.get_property("x")- PRE_CONTAINER.get_property("x"))
         MOVED_OBJECT.set_property("y",MOVED_OBJECT.get_property("y")- PRE_CONTAINER.get_property("y"))

         
      MOVED_OBJECT = None
      PRE_CONTAINER = None
      IMVEC.activeDoc.getCanvas().window.set_cursor(None)
      
      


   def on_mf_clicked(self,item,target_item,event):
      

      if IMVEC.activeDoc.getSelObject() != None:
         IMVEC.activeDoc.getSelObject().getSynObj().unselect()

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

         (abs_coord_x,abs_coord_y) = getAbsoluteCoords(IMVEC.activeDoc.getRootItem(),self.getO(),0,0)
         #COORDS_OFFSET = [ MOUSE_COORDS[0] - abs_coord_x ,  MOUSE_COORDS[1] - abs_coord_y]
         COORDS_OFFSET = [ MOUSE_COORDS[0] - self.getO().get_property("x") ,  MOUSE_COORDS[1] - self.getO().get_property("y")]
         synapseHistory.history.addHistory()



   #stops link line
   def on_input_clicked(self,item, target_item, event):
      global MAKE_LINE,NLPARAMETERS
      IMVEC.dbg.debug("INPUT CLICKED: %s",(item),dbg.DEBUG)

      if MAKE_LINE == 1:

         out_obj = IMVEC.activeDoc.getContainer().getMemberFromSynItem(NLPARAMETERS[0]).getSynObj() 
         in_obj = IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj()


         if (out_obj == in_obj):

            out_obj.setLoopMode(True)
            self.getLoopIcon().set_property("pixbuf",IMVEC.loopPixbuf)

         else:
            newitem = linkItem(IMVEC.activeDoc.getRootItem(),NLPARAMETERS[0],NLPARAMETERS[1],self,item)
            IMVEC.linkList.append(newitem)
            newobj = synlink("pipe%d" % len(IMVEC.linkList),out_obj,in_obj)
                                             
         
            newobj.setOutputNum(NLPARAMETERS[0].getOutNum(NLPARAMETERS[1]))
            newobj.setInputNum(self.getInNum(item))


            IMVEC.activeDoc.getContainer().append(linker(newobj,newitem))

            IMVEC.activeDoc.getContainer().updatePeers()
            IMVEC.activeDoc.refresh_objects_list()
         
                 
         MAKE_LINE=0
         del NLPARAMETERS[:]
         IMVEC.status_lbl.set_text("")

         for item in IMVEC.activeDoc.getContainer().getSynItems():
            try:
               item.changeInputsColor("#00CBFF")
            except:
               pass     


   #starts link line   
   def on_output_clicked(self,item, target_item, event):
      global MAKE_LINE, NLPARAMETERS
      if MAKE_LINE == 0:
         
         NLPARAMETERS.append(self)
         NLPARAMETERS.append(item)
         IMVEC.dbg.debug("OUTPUT CLICKED: %s",(item),dbg.DEBUG)
         
         IMVEC.status_lbl.set_text("Choose input object to link with %s" % (IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj().getName()))

         for item in IMVEC.activeDoc.getContainer().getSynItems():
            try:
               item.changeInputsColor("#00FF00")
            except:
               pass

         MAKE_LINE = 1


   def getMF(self):
      return self.mf

   def getIcon(self):
      return self.icon


   def getLoopIcon(self):

      return self.loop_icon

   def getO(self):

      return self.o
         
   def setText(self,text):

      self.ltext.set_property("text",text)

   def getLtext(self):
  
      return self.ltext


   def onLoopClicked(self,item,target_item,event):

      self.loop_icon.set_property("pixbuf",None)
      obj = IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj()
      obj.setLoopMode(False)



   def changeInputsColor(self,color):

       for inp in self.inputs:
         inp.set_property("fill_color",color)


   def connectMF(self):

      self.conns = list()

      self.conns.append(self.mf.connect("button-press-event",self.on_mf_clicked))
      self.conns.append(self.mf.connect("button-press-event",self.objectSelectionChange))
      
      
      if self.icon != None:

         self.conns.append(self.icon.connect("button-press-event",self.on_mf_clicked))
         self.conns.append(self.icon.connect("button-press-event",self.objectSelectionChange))
         

      
   def disconnectMF(self):

      self.mf.disconnect(self.conns[0])
      self.mf.disconnect(self.conns[1])

      if (self.icon != None):
         self.icon.disconnect(self.conns[2])
         self.icon.disconnect(self.conns[3])



   def connectAll(self):

      self.connectMF()
      self.conns.append(self.mf.connect("button-release-event",self.on_mf_released))
      if self.icon != None:
         self.conns.append(self.icon.connect("button-release-event",self.on_mf_released))

      for inp in self.inputs:
         inp.connect("button-press-event",self.on_input_clicked)
         inp.connect("enter-notify-event",self.on_inp_enter)
         inp.connect("leave-notify-event",self.on_conn_leave)
 
      for out in self.outputs:
         out.connect("button-press-event",self.on_output_clicked)
         out.connect("enter-notify-event",self.on_conn_enter)
         out.connect("leave-notify-event",self.on_conn_leave)


      try:
         self.loop_icon.connect("button-press-event",self.onLoopClicked)
      except:
         pass



   def on_inp_enter(self,item,target_item,event):
      global MAKE_LINE
      if MAKE_LINE == 1:
         IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.crossCursor)

   def on_conn_enter(self,item,target_item,event):
      global MAKE_LINE
      if MAKE_LINE == 0:
         IMVEC.activeDoc.getCanvas().window.set_cursor(IMVEC.crossCursor)

   def on_conn_leave(self,item,target_item,event):

      IMVEC.activeDoc.getCanvas().window.set_cursor(None)


   def getInput(self,n):

       return self.inputs[n]

   def getOutput(self,n):

      return self.outputs[n]


   def getOutNum(self,output):

      for i in range(0,len(self.outputs)):
         if output == self.outputs[i]:
            return i
            break
      IMVEC.dbg.debug("Output not found",tuple(),dbg.CRITICAL)

   def getInNum(self,inp):

      for i in range(0,len(self.inputs)):
         if inp == self.inputs[i]:
            return i
            break
      IMVEC.dbg.debug("Input not found",tuple(),dbg.CRITICAL)


class synappItem(synItem):


   def __init__(self,parent_canvas):


      self.tr_table_in = { 'right' : (135,40,180) , 'top' : (83,0,90), 'bottom' : (53,50,270) }
      self.tr_table_out = { 'left' : (0,25,180) , 'top' : (53,0,270), 'bottom' : (67,50,90) }
      

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,radius_x=10,radius_y=10, width=134, height=50,
				stroke_color="#cccccc", fill_color="#152233",tooltip="Application",
				line_width=4)

      self.pixbuf = IMVEC.appPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=52,y=10,pixbuf=self.pixbuf)

      self.loop_icon = goocanvas.Image(parent = self.o,x=115,y=32)
      


      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",-1)
      self.inputs[0].set_property("y",10)
      self.inputs[0].set_property("tooltip","Application's stdin")

      
      

      #self.inputs[0].set_property("fill-color-rgba",0x00cbffaa)
      #self.inputs[0].set_property("tooltip","Application's stdin")


      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1,tooltip="foo"))

      self.outputs[0].set_property("x",134)
      self.outputs[0].set_property("y",10)
      self.outputs[0].set_property("tooltip","Application's stdout/stderr (tty)")




      #self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 7 L 0 15 L 0 1 z",
                                      #stroke_color="black", fill_color="#ff3200", line_width=1))

      #self.outputs[1].set_property("x",134)
      #self.outputs[1].set_property("y",25)


      
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
      self.loop_icon = goocanvas.Image(parent = self.o,x=115,y=32)


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
      self.loop_icon = goocanvas.Image(parent = self.o,x=60,y=32)


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
      self.loop_icon = goocanvas.Image(parent = self.o,x=30,y=32)

    

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

      if IMVEC.activeDoc.getSelObject() != None:
         IMVEC.activeDoc.getSelObject().getSynObj().unselect()

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

      IMVEC.dbg.debug("MF_X_COORD: %d",(self.mf.get_property("x")),dbg.DEBUG)

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


      self.min_width = 190
      self.min_height = 50

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

      IMVEC.dbg.debug("MF_X_COORD: %d",(self.mf.get_property("x")),dbg.DEBUG)
      


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

      if IMVEC.activeDoc.getSelObject() != None:
         IMVEC.activeDoc.getSelObject().getSynObj().unselect()
      
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

      if self.o.get_property("y") == 0:

         self.h_extended = False

         self.o.set_property("y",-120)
         #self.sepLine1.set_property("y",-25)
         #self.sepLine2.set_property("y",-65)
         #self.mf.set_property("height",2)
         #self.showbtn.set_property("y",-118)
         #self.arrow.set_property("data","M 0 0 L 20 0 L 10 8 L 0 0 z")
         #self.arrow.set_property("x",5)
         #self.arrow.set_property("y",122)

         #self.titleLabel.set_property('fill_color_rgba',0xffffff00)
         #self.authorLabel.set_property('fill_color_rgba',0xffffff00)
         #self.dateLabel.set_property('fill_color_rgba',0xffffff00)
         #self.descrLabel.set_property('fill_color_rgba',0xffffff00)

         #lower the whole canvas of 118px
         if IMVEC.activeDoc != None:
            for item in IMVEC.activeDoc.getContainer().getSynItems():
               if item.getO().get_parent() == IMVEC.activeDoc.getRootItem():
                  item.getO().set_property("y",item.getO().get_property("y")-118)
          

      else:

         self.h_extended = True
         self.o.set_property("y",0)


         #self.mf.set_property("height",120)
         #self.showbtn.set_property("y",0)
         #self.sepLine1.set_property("y",25)
         #self.sepLine2.set_property("y",65)
         #self.arrow.set_property("data","M 0 8 L 10 0 L 20 8 L 0 8 z")
         
         #self.arrow.set_property("x",5)
         #self.arrow.set_property("y",122)

         #self.titleLabel.set_property('fill_color_rgba',0xffffffff)
         #self.authorLabel.set_property('fill_color_rgba',0xffffffff)
         #self.dateLabel.set_property('fill_color_rgba',0xffffffff)
         #self.descrLabel.set_property('fill_color_rgba',0xffffffff)


         #aise the whole canvas of 118px
         if IMVEC.activeDoc != None:
            for item in IMVEC.activeDoc.getContainer().getSynItems():
               if item.getO().get_parent() == IMVEC.activeDoc.getRootItem():
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

      self.o.set_property("x",0)
      self.o.set_property("y",0)

     
      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,width=self.root.get_property("width"), height=120, stroke_color="#8BA2BD", fill_color_rgba=0x8BA2BDAA,line_width=0)


      self.showbtn = goocanvas.Group(parent=self.o)

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

      self.dateLabel.connect("button-press-event",self.on_mf_clicked)
      self.dateLabel.connect("button-press-event",self.objectSelectionChange)

      self.titleLabel.connect("button-press-event",self.on_mf_clicked)
      self.titleLabel.connect("button-press-event",self.objectSelectionChange)

      self.authorLabel.connect("button-press-event",self.on_mf_clicked)
      self.authorLabel.connect("button-press-event",self.objectSelectionChange)

      self.descrLabel.connect("button-press-event",self.on_mf_clicked)
      self.descrLabel.connect("button-press-event",self.objectSelectionChange)


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

      self.min_width = 170
      self.min_height = 50


      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.inputs = list()
      self.outputs = list()

      self.mf = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=15, radius_y=15,width=200, height=100,
				stroke_color="#cccccc", fill_color_rgba=0x333333aa,
				line_width=0)

      self.ltext = goocanvas.Text(parent = self.o, font="Sans 10" , text="this is a comment box", x=15, y=20,
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



   def on_exporticon_enter(self,item,target_item,event):

      self.exporticon.set_property("pixbuf",IMVEC.exportOverPixbuf)

   def on_exporticon_leave(self,item,target_item,event):

      self.exporticon.set_property("pixbuf",IMVEC.exportPixbuf)


   def on_playicon_enter(self,item,target_item,event):

      if self.running:

         self.playicon.set_property("pixbuf",IMVEC.cstopOverPixbuf)

      else:

         self.playicon.set_property("pixbuf",IMVEC.cplayOverPixbuf)

   def on_playicon_leave(self,item,target_item,event):

      if self.running:
         self.playicon.set_property("pixbuf",IMVEC.cstopPixbuf)
      else:
         self.playicon.set_property("pixbuf",IMVEC.cplayPixbuf)

   def on_playicon_clicked(self,item,target_item,event):

      self_synobj_ref = IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj()
      if not self.running: 
         self_synobj_ref.updateObjList()
         IMVEC.engine.playWorkflow(self_synobj_ref.getObjList())
         self.playicon.set_property("pixbuf",IMVEC.cstopPixbuf)
         self.running = True
      else:
         IMVEC.engine.stopWorkflow(self_synobj_ref.getObjList())
         self_synobj_ref.flushObjList()
         self.playicon.set_property("pixbuf",IMVEC.cplayPixbuf)
         self.running = False
         



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


      self.running = False

      

      self.min_width = 200
      self.min_height = 100

      self.outputs = list()
      self.inputs = list()


      self.pixbuf = IMVEC.containerPixbuf
      self.exportPixbuf = IMVEC.exportPixbuf
      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.inputs = list()
      self.outputs = list()

     
      self.mf = goocanvas.Rect(parent = self.o, x=5, y=5, radius_x=15, radius_y=15,width=300, height=200,
				stroke_color="#cccccc", fill_color_rgba=0x151515dd,
				line_width=4)


      self.icon = goocanvas.Image(parent = self.o,x=0,y=0,pixbuf=self.pixbuf)
      self.replaceIcon()


      self.head = goocanvas.Rect(parent = self.o, x=6, y=6,radius_x=14, radius_y=14, width=200, height=35,
				stroke_color="#cccccc", fill_color_rgba=0xcccccccc,
				line_width=0)
      

      
     

     
      self.exporticon = goocanvas.Image(parent = self.o,x=44,y=7,pixbuf=self.exportPixbuf)
      self.playicon = goocanvas.Image(parent = self.o,x=10,y=7,pixbuf=IMVEC.cplayPixbuf)



      self.ltext = goocanvas.Text(parent = self.o, font="Sans 8" , text="foobar", x=80, y=17,
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


      self.playicon.connect("enter-notify-event",self.on_playicon_enter)
      self.playicon.connect("leave-notify-event",self.on_playicon_leave)
      self.playicon.connect("button-press-event",self.on_playicon_clicked)



      self.exporticon.connect("enter-notify-event",self.on_exporticon_enter)
      self.exporticon.connect("leave-notify-event",self.on_exporticon_leave)




class reportItem(synItem):


   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,radius_x=10,radius_y=10, width=50, height=50,
				stroke_color="#cccccc", fill_color="#dadada",
				line_width=4)

      self.pixbuf = IMVEC.reportPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=10,y=10,pixbuf=self.pixbuf)

    

      self.inputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.inputs[0].set_property("x",0)
      self.inputs[0].set_property("y",10)
 
      self.ltext = goocanvas.Text(parent = self.o, text="", x=3, y=-15,
						width=100,font="sans 8", fill_color="#dadada")

      self.connectAll()





class labelItem(synItem):


   def on_t_valid(self,widget):

      new_input = self.inpd.getInput()
      self.inpd.getWindow().hide()

      IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj().setContent(new_input)

      self.content_label.set_property("text",new_input)


   def on_clickable_change(self,item,target_item,event):

      self.inpd = inputDialog("Please enter a label Value")
      self.inpd.setCallBack(self.on_t_valid)
      self.inpd.run()


      
     
   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.clickable = goocanvas.Rect(parent = self.o, x=0, y=10,radius_x=10,radius_y=10, width=150, height=30,
				stroke_color="#cccccc", fill_color_rgba=0x151515dd,
				line_width=1)

      self.mf = goocanvas.Rect(parent = self.o, x=138, y=0,radius_x=10,radius_y=10, width=50, height=50,
				stroke_color="#cccccc", fill_color="#c5264f",
				line_width=4)

      self.pixbuf = IMVEC.labelPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=148,y=10,pixbuf=self.pixbuf)

    

      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",188)
      self.outputs[0].set_property("y",10)
 
      self.ltext = goocanvas.Text(parent = self.o, text="", x=3, y=-10,
						width=100,font="sans 8", fill_color="#c5264f")


      self.content_label = goocanvas.Text(parent = self.o, text="Click Here To set Value", x=10, y=18,
						width=150,font="sans 8", fill_color="#dadada")



      self.connectAll()
      self.clickable.connect("button-press-event",self.on_clickable_change)
      self.content_label.connect("button-press-event",self.on_clickable_change)



class kbdItem(synItem):



   def lock(self):
 
      self.content_label.set_property("text","Keyboard\nAcquired")
      self.content_label.set_property("fill_color","#00FF00")

   
   def unlock(self):

      self.content_label.set_property("text","Acquire\nKeyboard")
      self.content_label.set_property("fill_color","#dadada")

      
   def on_clickable_change(self,item,target_item,event):

      kbd_object = IMVEC.activeDoc.getContainer().getMemberFromSynItem(self).getSynObj()

      if not kbd_object.getInputLock():
 
         if IMVEC.activeDoc.getKeyboard() != None:

            prev_kbd_object = IMVEC.activeDoc.getKeyboard()
            prev_kbd_item = IMVEC.activeDoc.getContainer().getMemberFromSynObj(prev_kbd_object).getSynItem()

            prev_kbd_item.unlock()
            prev_kbd_object.setInputLock(False)
       
         
         IMVEC.activeDoc.setKeyboard(kbd_object)
         kbd_object.setInputLock(True)
         self.lock()
     

      else:
         kbd_object.setInputLock(False)
         self.unlock()
         IMVEC.activeDoc.setKeyboard(None)
   

  
   def __init__(self,parent_canvas):

      self.outputs = list()
      self.inputs = list()

      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)


      self.clickable = goocanvas.Rect(parent = self.o, x=10, y=40,radius_x=10,radius_y=10, width=80, height=40,
				stroke_color="#cccccc", fill_color_rgba=0x151515dd,
				line_width=1)

      self.mf = goocanvas.Rect(parent = self.o, x=0, y=0,radius_x=10,radius_y=10, width=100, height=50,
				stroke_color="#cccccc", fill_color="#5591ff",
				line_width=4)

      self.pixbuf = IMVEC.kbdPixbuf
      self.icon = goocanvas.Image(parent = self.o,x=35,y=10,pixbuf=self.pixbuf)

    

      self.outputs.append(goocanvas.Path( parent = self.o,data="M 0 0 L 10 15 L 0 30 L 0 1 z",
                                      stroke_color="black", fill_color="#00cbff", line_width=1))

      self.outputs[0].set_property("x",100)
      self.outputs[0].set_property("y",10)
 
      self.ltext = goocanvas.Text(parent = self.o, text="", x=3, y=-15,
						width=100,font="sans 8", fill_color="#5591ff")


      self.content_label = goocanvas.Text(parent = self.o, text="Acquire\nKeyboard", x=23, y=53,
						width=150,font="sans 8", fill_color="#dadada")



      self.connectAll()
      self.clickable.connect("button-press-event",self.on_clickable_change)
      self.content_label.connect("button-press-event",self.on_clickable_change)










class selItem:


   def on_mf_clicked(self,item,target_item,event):
      
      global MOVED_OBJECT
      global COORDS_OFFSET
      global MOUSE_COORDS
      global ACTIVE_OBJECT

      if (item != None):
         MOVED_OBJECT = self.getO()
         ACTIVE_OBJECT = self

         synapseHistory.history.addHistory()
         (abs_coord_x,abs_coord_y) = getAbsoluteCoords(IMVEC.activeDoc.getRootItem(),self.getO(),0,0)
         #COORDS_OFFSET = [ MOUSE_COORDS[0] - abs_coord_x ,  MOUSE_COORDS[1] - abs_coord_y]

         COORDS_OFFSET = [ MOUSE_COORDS[0] - self.getO().get_property("x") ,  MOUSE_COORDS[1] - self.getO().get_property("y")]



   def getO(self):

      return self.o

   def getMF(self):

      return self.mf

   def __init__(self,parent_canvas):


      self.root = parent_canvas
      self.o = goocanvas.Group(parent=self.root)

      self.mf = goocanvas.Rect(parent = self.o, x=IMVEC.mouseCoords[0], y=IMVEC.mouseCoords[1], radius_x=0, radius_y=0,width=0, height=0,
      stroke_color="#0099cc", fill_color_rgba=0x40ddff90,
      line_width=1)


