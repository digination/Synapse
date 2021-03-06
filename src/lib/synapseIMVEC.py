import pygtk
pygtk.require("2.0")
import gtk
import os
from synapseDebug import dbg
from synapseEngine import synapseEngine



#Inter modules Variables exchange Class
class IMVEC:

   dbg = None;
   cfg = None;

   has_webkit = 0
   HAS_XMPP = 0
   HAS_SCAPY = 0
   
   #application clipboard.
   cb =  gtk.Clipboard(gtk.gdk.display_get_default(),"CLIPBOARD")

   engine = None

   #gtk widget references shared by both main and canvas modules
   obrowser = None
   oprop = None
   status_lbl = None

   #Document global variables
   docList = list()
   activeDoc = None

   linklist = list()

   #canvas mouse coords
   mouseCoords = list()
   
   makeLine = 0
   
   aboutWindow = None


   RES_PATH = "/usr/share/synapse"

   libpaths = list()
   libpaths.append(os.path.expanduser("~"))
   pkgMgr = None
   libtree = None

   unsavedDocs = dict()


   folderPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/folder.png" % (RES_PATH),16,16)   


   wfPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/synwf.png" % (RES_PATH),16,16)
   
   appPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/synappItem.png" % (RES_PATH),32,32)
   servPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/servItem.png" % (RES_PATH),32,32)
   timerPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/timerItem.png" % (RES_PATH),32,32)
   injectorPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/injectItem.png" % (RES_PATH),32,32)
   testPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/testItem.png" % (RES_PATH),32,32)
   demuxPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/demuxItem.png" % (RES_PATH),32,32)
   muxPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/muxItem.png" % (RES_PATH),32,32)
   commentPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/commentItem.png" % (RES_PATH),32,32)
   filterPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/filterItem.png" % (RES_PATH),32,32)
   monitorPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/monitorItem.png" % (RES_PATH),32,32)
   containerPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/containerItem.png" % (RES_PATH),32,32)
   reportPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/reportItem.png" % (RES_PATH),32,32)
   dbPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/dbItem.png" % (RES_PATH),32,32)
   dbPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/dbItem.png" % (RES_PATH),16,16)  
   
   kbdPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/keyboard.png" % (RES_PATH),32,32)
   kbdPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/keyboard.png" % (RES_PATH),16,16)
   
   
   pyPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/python.png" % (RES_PATH),32,32)
   pyPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/python.png" % (RES_PATH),16,16)
   
   xmppPixbuf =  gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/xmpp.png" % (RES_PATH),32,32)
   xmppPixbuf_s =  gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/xmpp.png" % (RES_PATH),16,16)
   
   scapyPixbuf =  gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/scapy.png" % (RES_PATH),32,32)
   scapyPixbuf_s =  gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/scapy.png" % (RES_PATH),16,16)
   
   
   
   labelPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/64/labelItem.png" % (RES_PATH),32,32)
   exportPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/32/export.png" % (RES_PATH),32,32)
   exportOverPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/32/export_over.png" % (RES_PATH),32,32)
   cplayPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/cplay.png" % (RES_PATH),32,32)
   cplayOverPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/cplay_over.png" % (RES_PATH),32,32)
   cstopPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/cstop.png" % (RES_PATH),32,32)
   cstopOverPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/cstop_over.png" % (RES_PATH),32,32)
   
   
   appPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/synappItem.png" % (RES_PATH),16,16)
   servPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/servItem.png" % (RES_PATH),16,16)
   timerPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/timerItem.png" % (RES_PATH),16,16)
   injectorPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/injectItem.png" % (RES_PATH),16,16)
   testPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/testItem.png" % (RES_PATH),16,16)
   demuxPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/demuxItem.png" % (RES_PATH),16,16)
   muxPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/muxItem.png" % (RES_PATH),16,16)
   commentPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/commentItem.png" % (RES_PATH),16,16)
   filterPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/filterItem.png" % (RES_PATH),16,16)
   monitorPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/monitorItem.png" % (RES_PATH),16,16)
   containerPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/containerItem.png" % (RES_PATH),16,16)
   reportPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/reportItem.png" % (RES_PATH),16,16)
     
    
   
   
   labelPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/64/labelItem.png" % (RES_PATH),16,16)
   
   
   resizePixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/32/resize.png" % (RES_PATH),16,16)
   
   monitorMaximizePixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/16/monMax.xpm" % (RES_PATH),16,16)
   monitorHidePixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/16/monHide.xpm" % (RES_PATH),16,16)
   
    
   linkPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/linkItem.png" % (RES_PATH),16,16)
   synapse_logo = gtk.gdk.pixbuf_new_from_file("%s/images/synapse.png" % (RES_PATH))
   loopPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/128/loop.png" % (RES_PATH),16,16)  
   cpuPixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/48/cpu.png" % (RES_PATH),16,16) 
   
   
   ioleft = gtk.gdk.pixbuf_new_from_file("%s/images/io_left.png" % (RES_PATH));
   ioright = gtk.gdk.pixbuf_new_from_file("%s/images/io_right.png" % (RES_PATH));
   iotop = gtk.gdk.pixbuf_new_from_file("%s/images/io_top.png" % (RES_PATH));
   iobottom = gtk.gdk.pixbuf_new_from_file("%s/images/io_bottom.png" % (RES_PATH));
   
   bbhoriz = gtk.gdk.pixbuf_new_from_file("%s/images/bb_horiz.png" % (RES_PATH));
   
   
   #Help Browser Icons
   arrow_l = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/64/arrow_l.png" % (RES_PATH),20,20)
   arrow_r = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/64/arrow_r.png" % (RES_PATH),32,20)
   doc_search = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/64/search.png" % (RES_PATH),20,20)
   
   
   
   extendCursor = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
   plusCursor = gtk.gdk.Cursor(gtk.gdk.PLUS)
   crossCursor = gtk.gdk.Cursor(gtk.gdk.TCROSS)
