import gtk
import os

#Inter modules Variable exchange Class
class IMVEC:

   running = False

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


   monitorMaximizePixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/16/monMax.xpm" % (RES_PATH),16,16)
   monitorHidePixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/16/monHide.xpm" % (RES_PATH),16,16)


   linkPixbuf_s = gtk.gdk.pixbuf_new_from_file_at_size("%s/icons/256/linkItem.png" % (RES_PATH),16,16)

   synapse_logo = gtk.gdk.pixbuf_new_from_file("%s/images/synapse.png" % (RES_PATH))

