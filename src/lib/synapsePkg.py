from synapseIMVEC import *
import shutil
import tarfile
import os
import shutil
import glob
import hashlib
import gtk
import gobject

class pkgManager:

   def getTreeStore(self):
      return self.treestore


   def setColumnStr(self,treeviewcolumn, cell, model, iter):
      string = model.get_value(iter, 1)
      cell.set_property('text', string )
      return


   def setColumnPixbuf(self,treeviewcolumn, cell, model, iter):
      string = model.get_value(iter, 0)
      cell.set_property('pixbuf', string )
      return


   def populateTreeStore(self):
      
      self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf,gobject.TYPE_STRING)
     
      pkgs =  os.listdir('/tmp/synapse')  
     
      for pkg in pkgs:
         print "pkg: %s" % (pkg)
         pkgsha1 = pkg.split("/").pop()
         print "pkgsha: %s" % (pkgsha1)
         for msha1,member in self.members.items():
            if pkgsha1 == msha1:
               print "FOUND %s" % (msha1)
               tsname = "%s (%s)" % (member.getName(),msha1)
               iter = self.treestore.append(None,[IMVEC.folderPixbuf_s,tsname] )
               self.treestore.append(iter,[IMVEC.folderPixbuf_s,"building_blocks"])
               self.treestore.append(iter,[IMVEC.folderPixbuf_s,"modules"])
               iter = self.treestore.append(iter,[IMVEC.folderPixbuf_s,"workflows"])
               
               mworkflows = glob.glob("/tmp/synapse/%s/workflows/*.sws" % (msha1) )
               for mworkflow in mworkflows:
                  name = mworkflow.split("/").pop().rstrip(".sws")
                  self.treestore.append(iter,[IMVEC.wfPixbuf_s,name])
                  

   def getMember(self,sha1):
      return self.members[sha1]
      
   def __init__(self):

      self.members = dict()

      #create tmp directory to store uncompressed pkg data
      try:
         if os.path.exists("/tmp/synapse"):
            shutil.rmtree("/tmp/synapse")
         os.mkdir("/tmp/synapse")
      except:
         print "cannot create tmp directory in /tmp, skipping pkg load.."
         return

      for libpath in IMVEC.libpaths:

         for filename in glob.glob( os.path.join(libpath, '*.spkg') ):

            newpkg = synpkg(filename)
            newpkg.computeSHA1()
            #compares with current list to see if sha1 already exists
            for msha1,member in self.members.items():

               if newpkg.getSHA1() == msha1:
                  print "Package %s Already imported, skipping.." % (filename)
                  newpkg = None
                  break
      
            if newpkg != None:

               try:
                  #creates new directory in tmp that will contain our uncompressed pkg files
                  os.mkdir("/tmp/synapse/%s" % (newpkg.getSHA1()) )
                  #perform detar
                  tar = tarfile.open(filename,mode="r:gz")
                  tar.extractall(path="/tmp/synapse/%s" % (newpkg.getSHA1()) )
                  tar.close()
               except:
                  print "cannot open or extract synapse pkg file: %s" % (filename)
                  newpkg = None

            if newpkg != None:
               newpkg_name = filename.split("/").pop().rstrip(".spkg")
               newpkg.setName(newpkg_name)
               self.members[newpkg.getSHA1()] = newpkg

      self.populateTreeStore()
            
             

class synpkg:

   #we use sha in order to produce pkg uniq id
   def computeSHA1(self):

      try:
         f = open(self.pkgfile)
         h = hashlib.sha1()
         h.update(f.read())
         self.SHA1 = h.hexdigest()
         f.close()
      except:
         print "Cannot compute sha1 digest for archive: %s" % (self.pkgfile)



   def setName(self,name):
      self.name = name
    
   def getName(self):
      return self.name
        
   def getPkgFile(self):
      return self.pkgfile
   def getSHA1(self):
      return self.SHA1

   def __init__(self,pkgfile):
      self.pkgfile = pkgfile
      self.name = ""
      self.comment = ""
      
