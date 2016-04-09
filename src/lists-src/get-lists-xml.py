#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

###############################################################
# Imports
###############################################################
import sys  # stdin, stdout, stderr
import re
import xml.etree.ElementTree as ET

###############################################################
# Method for extract pages with prefix 'List of' from xml dump
###############################################################
def getListPage():
  indentLevel = "\t"
  listRegex = re.compile(r'List of',re.I)
  count = 0

  isListPage = False
  counter = 0

  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/List_of/ExtractedLists.xml','w+')
  file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  print 'Začíná parsing...'
  # parsování data
  for event, elem in ET.iterparse('/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20160113-pages-articles.xml'):
    if event == 'end':
      if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
        counter += 1
        if listRegex.search(elem.text):
          count += 1
          isListPage = True
          count += 1
          file.write('<page>\n')
          file.write(indentLevel+'<title>'+unicode(elem.text).encode('utf-8')+'</title>\n')
        elif isListPage:
          #file.close()
          isListPage = False
        else:
          isListPage = False
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}timestamp" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('\t<'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}username" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        indentLevel = '\t\t'
        file.write('\t<contributor>\n\t\t</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}id" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        if indentLevel == '\t\t':
          file.write(indentLevel+'<'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n\t</contributor>\n')
        else:
          file.write(indentLevel+'<'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('</page>\n')
        indentLevel = '\t'
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}sha1" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('\t<revision>\n\t\t</'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n\t</revision>\n')
      elif elem.tag != "{http://www.mediawiki.org/xml/export-0.10/}contributor" and elem.tag != "{http://www.mediawiki.org/xml/export-0.10/}revision" and isListPage:
        tag = elem.tag.replace('{http://www.mediawiki.org/xml/export-0.10/}','')
        file.write('\t<'+tag+'>'+unicode(elem.text).encode('utf-8')+'</'+tag+'>\n')
    elem.clear()  # discard the element

  file.close()
  print "\nCelkový počet článků: ", counter
  print "\nCelkový počet nalezených listů: ", count
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

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  # parsování
  getListPage()

  print "Done"

  sys.exit(0)
