#!/bin/sh

rm ui/*.xml

for i in `ls glade|grep glade` ; do

	gtk-builder-convert glade/$i ui/$i

	rename 's/.glade/.xml/' ui/*

 
done
