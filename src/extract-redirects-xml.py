#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import sys  # stdin, stdout, stderr
import re
import os
import subprocess

# import XML parse
import xml.etree.ElementTree as ET

# FUNKCE parseOut
# funkce pro zpracování výstupu dotazovače pomocí regexu
# @param result - výstup z dotazovače
# @return out - výstupní zpracovaný text
def findRedirects():
  pageTitle = ""

  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/redirectedLinks.links','w+')
  print 'Začíná parsing...'
  # parsování data
  for event, elem in ET.iterparse('/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20160113-pages-articles.xml'):
  #for event, elem in ET.iterparse('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/test-sorted.xml'):
    if event == 'end':
      if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
        pageTitle = unicode(elem.text).encode('utf-8')
        #print "title"
        #print pageTitle
        #p = subprocess.Popen(['grep','-n', '-s',entityURL,'/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/all-wiki-links.aux'],stdout=subprocess.PIPE)
        #output = p.communicate()[0]
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}redirect":
        #print "redirect"
        #print elem.attrib['title']
        #if ' ' in pageTitle:
        pageRedirect = unicode(elem.attrib['title'].replace(' ','_')).encode('utf-8')
        file.write('https://en.wikipedia.org/wiki/'+pageTitle.replace(' ','_')+'\thttps://en.wikipedia.org/wiki/'+pageRedirect+'\n')
        #file.write('\t<'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
    elem.clear()  # discard the element

  file.close()

# main
if __name__ == "__main__":
  # parsování
  findRedirects()

  print "Done"

  sys.exit(0)
