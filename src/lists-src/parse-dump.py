#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import sys  # stdin, stdout, stderr
import re
import os
import subprocess
import nltk

# import XML parse
import xml.etree.ElementTree as ET

# FUNKCE parseOut
# funkce pro zpracování výstupu dotazovače pomocí regexu
# @param result - výstup z dotazovače
# @return out - výstupní zpracovaný text
def getListPage():
  level = "\t"
  xmlFile = ""
  #List of Latin words with English derivatives
  listRegex = re.compile(r'List of Latin words with English derivatives|List of United States cities by population',re.I)

  count = 0

  isListPage = False
  counter = 0

  print 'Začíná parsing...'
  # parsování data
  for event, elem in ET.iterparse('/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20160113-pages-articles.xml'):
    if count > 1:
      print "Nalezeny všechny výsledky, ukončuji program..."
      return

    if event == 'end':
      if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        #print elem.text
        counter += 1
        if counter % 10000 == 0:
          print "Zpracováno: {}".format(counter)
        if listRegex.search(elem.text):
          count += 1
          isListPage = True
          print "Stránka nalezena!\nVytvářím soubor..."
          file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/List_of/'+elem.text.replace(' ','_')+'.xml','w+')
          file.write('<?xml version="1.0" encoding="UTF-8"?>\n<page>\n')
          file.write(level+'<title>'+unicode(elem.text).encode('utf-8')+'</title>\n')
          xmlFile = ""
        elif isListPage:
          print "Zavírám soubor..."
          file.close()
          isListPage = False
        else:
          isListPage = False
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}timestamp" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('\t</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}username" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        level = '\t\t'
        file.write('\t<contributor>\n\t\t</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}id" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        if level == '\t\t':
          file.write(level+'</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n\t</contributor>')
        else:
          file.write(level+'</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('</page>')
      elif elem.tag != "{http://www.mediawiki.org/xml/export-0.10/}contributor" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('\t</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
    elem.clear()  # discard the element

  print "\nCelkový počet článků: ", counter
  print "Done"


# Funkce pro vyčištění textu v XML
# @param - elem - element
# @return - elem.text - zformátovaný text
def clearText2(text):
  # smazání přebytečných věcí
  # Původní verze co jsem měl - možná se bude hodit
  text = re.sub('-->', '#', text)
  # Nahrazení <ref>.. znaky ř a ž a smazání mezi nimi - funguje
  text = re.sub('<ref[^>]*/>', '', text)
  text = re.sub('(<ref[^>]*>)|(<!--<ref[^>]*>)', 'ř', text)
  text = re.sub('</ref>', 'ž', text)
  text = re.sub('ř[^ž]*ž', '', text)
  # nahradí tag <!--...-->
  text = re.sub('-->', '#', text)
  text = re.sub('<!--[^#]*#', '', text)

  # TODO - ???
  ###elem.text = re.sub('-->','#',elem.text)
  '''elem.text = re.sub('(<!--<ref[^>]*>[^<]*</ref>)|(<ref[^>]*>[^<]*</ref>)|(<ref[^/]*/>)','',elem.text)
  elem.text = re.sub('<!--[^#]*#','',elem.text)
  elem.text = re.sub('(<!--<ref[^>]*>[^<]*</ref>)|(<ref[^>]*>[^<]*</ref>)|(<ref[^/]*/>)','',elem.text)'''

  # File/Image + <!--...--> + {{...}}
  text = re.sub('\[\[(File|Image):[^\n]*\n*', '', text)
  # elem.text = re.sub('\[\[(File|Image):[^\]]*\]\]','',elem.text)
  # kudrnaté závorky
  # elem.text = re.sub('\{\{[^\}]*\}\}\n*','',elem.text)
  text = re.sub('\{\{[^q|l][^\}]*\}\}\n*', '', text)
  # odfiltrování uvozovek, mezer
  text = re.sub('\'{2,6}', '', text)
  text = re.sub('\n{2,6}', '\n', text)
  text = re.sub('\n={2,6}', '\n\n===', text)
  # odstranění referencí atd. (nepotřebné)
  text = re.sub('={2,}References[^\0]*', '', text)

  return text


def clearText(text):
  text = re.sub('<ref[^>]*\/>', '', text)  # Clear short tags
  openRef = re.compile("(<!--[ ]*<ref[^>]*>)|(<ref[^>]*>)")  # Open tag
  closeRef = re.compile("<\/ref>")  # Close tag

  openTag = openRef.search(text)
  closeTag = closeRef.search(text)

  while openTag != None and closeRef != None:
    text = text[:openTag.start()] + text[closeTag.end():]
    openTag = openRef.search(text)
    closeTag = closeRef.search(text)

  text = re.sub('\{\{[^q|l][^\}]*\}\}\n*', '', text)
  text = re.sub('<!--[^>]*>', '', text)
  text = re.sub('\[\[(File|Image):[^\n]*\n*', '', text)
  text = re.sub('&nbsp;', '', text)

  # odfiltrování uvozovek, mezer
  text = re.sub('\'{2,6}', '', text)
  text = re.sub('\n{2,6}', '\n', text)
  text = re.sub('\n={2,6}', '\n\n===', text)
  # odstranění referencí atd. (nepotřebné)
  text = re.sub('={2,}References[^\0]*', '', text)

  return text

# main
if __name__ == "__main__":
  # parsování
  getListPage()

  print "Done"

  sys.exit(0)
