#!/usr/bin/env python

import os
import sys
import shutil

LANG="en"


class syndocobj:

  name = ""
  behaviour = ""
  icon = ""
  resizable = ""
  


class syndocopt:

  def __init__(self,oname,otype,odefault,odescr):

    self.name = oname
    self.type = otype
    self.default = odefault
    self.descr = odescr

  def getAll(self):

    return (self.name,self.type,self.default,self.descr)




 
def parse_obj_option(option_content):

  oname = ""
  otype = ""
  odefault = ""
  odescr = ""

  descr_ruptor = 0



  for line in option_content:
    line = line.rstrip("\n")

    if line.find("end_descr") == 0 :

      descr_ruptor = 0

    if line.find("option_title") == 0 :

      oname = line.lstrip("option_title ")

    if line.find("option_type") == 0 :

      otype = line.lstrip("option_type ")

    if line.find("option_default") == 0:

      odefault = line.lstrip("option_default ")

    if descr_ruptor == 1:

      odescr += line

    if line.find("option_descr") == 0 :

      descr_ruptor = 1


  return syndocopt(oname,otype,odefault,odescr)


def parse_obj_data(descr_file):

  dfh = open("data/%s/objects/%s" % (LANG,descr_file),"r")

  lines = dfh.readlines()

  behav_ruptor = 0
  opt_ruptor = 0

  options_list = list()
  option_content = list()


  for line in lines:

    if line.find("end_behaviour") == 0:

      behav_ruptor = 0

    if line.find("end_option") == 0:

      options_list.append(parse_obj_option(option_content))
      option_content = list()
      opt_ruptor = 0


    if line.find("object_name") == 0 :

      syndocobj.name = line.lstrip("object_name ")

    if line.find("resizable") == 0 :

      syndocobj.resizable = line.lstrip("resizable ")


    if line.find("icon") == 0 :

      syndocobj.icon = line.lstrip("icon ")

    if behav_ruptor == 1:

      syndocobj.behaviour += line

    if opt_ruptor == 1:

      option_content.append(line)
      


    if line.find("behaviour") == 0:

      behav_ruptor = 1

    if line.find("option") == 0:

      opt_ruptor = 1

  return options_list

    

def compile_object_pages():

  object_files = os.listdir("data/%s/objects" % (LANG))
  
  tfh = open("templates/%s/object.tpl" % (LANG),"r")
  otfh = open("templates/%s/option.tpl" % (LANG),"r")


  #get template content
  template_lines = tfh.readlines()
  template_content = ""

  for tpl_line in template_lines:

    template_content = template_content + "\n" + tpl_line


  #get option template content
  otemplate_lines = otfh.readlines()
  otemplate_content = ""

  for otpl_line in otemplate_lines:

    otemplate_content = otemplate_content + "\n" + otpl_line



  #processes each object data file
  for obj_file in object_files:

    syndocobj.behaviour = ""
    olist = parse_obj_data(obj_file)

    html_content = template_content

    #replace template markups by real informations
    html_content = html_content.replace("[OBJECT_NAME]",syndocobj.name)
    html_content = html_content.replace("[OBJECT_ICON]",syndocobj.icon)
    html_content = html_content.replace("[BEHAVIOUR]",syndocobj.behaviour)
    html_content = html_content.replace("[RESIZABLE]",syndocobj.resizable)


    html_file = obj_file[:len(obj_file) - 6 ] + ".html"

    #write generated content to file
    hfh = open("%s/html/%s" % (LANG,html_file),"w+")
    hfh.write(html_content)


    for opt in olist:

      (oname,otype,odefault,odescr) = opt.getAll()
 
      html_content = otemplate_content
      html_content = html_content.replace("[OPTION_NAME]",oname)
      html_content = html_content.replace("[OPTION_TYPE]",otype)
      html_content = html_content.replace("[DEFAULT_VALUE]",odefault)
      html_content = html_content.replace("[OPTION_DESCR]",odescr)
      hfh.write(html_content)

    hfh.close()





def compile_main_pages():

  page_files = os.listdir("data/%s/pages" % (LANG))
  mtfh = open("templates/%s/main.tpl" % (LANG),"r")


  #get template content
  template_lines = mtfh.readlines()
  template_content = ""

  for tpl_line in template_lines:

    template_content = template_content + "\n" + tpl_line


  
  #processes each page data file
  for page_file in page_files:

    print page_file

    page_fh = open("data/%s/pages/%s" %(LANG,page_file),"r")

    page_lines = page_fh.readlines()
    page_content = ""

    for page_line in page_lines:

      page_content = page_content + "\n" + page_line
    

    html_file = page_file[:len(page_file) - 6 ] + ".html"
    page_title = page_file[:len(page_file) - 6 ].replace("_"," ") 
    
    print html_file

    html_content = template_content
    #replace template markups by real informations
    html_content = html_content.replace("[PAGE_TITLE]",page_title)
    html_content = html_content.replace("[PAGE_CONTENT]",page_content)
    
   
    #write generated content to file
    hfh = open("%s/html/%s" % (LANG,html_file),"w+")
    hfh.write(html_content)
    hfh.close()



    
if __name__ == "__main__":

  compile_object_pages()
  compile_main_pages()

