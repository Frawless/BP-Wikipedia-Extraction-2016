#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import subprocess
import argparse
import re
import glob

import socket

# import of created moduls
import find
import persons


# Function for clear page TODO - smazat tvorbu čistého textu (asi)
def clearPage(page):
  pageTag = False
  parsedPage = ""
  pureText = ""
  page = page.split("\n")
  for line in page:
    # For entity type (person, event, artist, location....)
    if pageTag:
      tmp = re.search(r'\d+\s+([^\s]+\s+){14}', line)  # LF nertag
      if tmp:
        if "0" not in tmp.group(1):
          parsedPage = parsedPage + " entity=" + tmp.group(1)
      tmp = re.search(r'\d+\s+([^\s]+\s+){9}', line)  # LF nertag
      if tmp:
        if "0" not in tmp.group(1):
          parsedPage = parsedPage + " URL=" + tmp.group(1)

    if "%%#PAGE" in line:
      pageTag = True
      parsedPage += line
      pureText = parsedPage  # option for pure text (delete)

    if "%%#SEN" in line:
      parsedPage += "\n"
      pureText = pureText.replace(' .|G__', '.').replace(' .', '.') + "\n"  # option for pure text (delete)
      pageTag = False
      continue

    if not pageTag:
      tmp = re.search(r'^\d+\s+([^\s]+\s+[^\s]+\s+[^\s]+)',line)  # token + tag + lemma - can be modifed for another options
      tmp_nertag = re.search(r'\d+\s+([^\s]+\s+){14}', line)  # LF nertag
      tmp_url = re.search(r'\d+\s+([^\s]+\s+){9}', line)
      if tmp_nertag and tmp and tmp_url:
        if "0" not in tmp_nertag.group(1) and "0" not in tmp_url.group(1):
          parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|entity=" + tmp_nertag.group(1)[:-1] + "|URL=" + tmp_url.group(1)[:-1] + "]] "
        elif "0" in tmp_nertag.group(1) and "0" not in tmp_url.group(1):
          parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|URL=" + tmp_url.group(1)[:-1] + "]] "
        elif "0" not in tmp_nertag.group(1) and "0" in tmp_url.group(1):
          parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|entity=" + tmp_nertag.group(1)[:-1] + "]] "
        else:
          parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "]] "
  return parsedPage

# Method for TODO
def getInformationFromPage(file, task_list):
  for line in file:
    if "%%#PAGE" in line:
      # extract text
      if len(array) > 0:
        outputTags = clearPage(page)
        #print outputTags
        # print outputText
        if "%%#PAGE Influence" in pageTitle:
          task_list = find.checkInfluencePages(outputTags, array, task_list)
        else:
          task_list = find.checkInformation(outputTags, array, task_list)
        outputTags = ""
        del array[:]  # delete finding array
      # task creation
      for task in task_list:
        tmp = task
        task = task.split('|')
        if "->" not in tmp:  # na serveru knot11 to z nejazných důvodů spadne na správné konstrukci tasku
          if 'PAGE ' + task[0].replace('entity=', '') + '\thttp' in line and 'verb=' in task[1]:  # pages "entity"
            # 0./-if task[0].replace('entity=','')+'\thttp' in line:
            array.append(tmp)
          elif task[0].replace('entity=', '') in line and 'verb=' not in task[1]:  # pages ..."entity"
            array.append(tmp)
          elif task[0].replace('entity=', '') in line and 'task=' in task[2]:  # pages ..."entity1" (influence)
            array.append(tmp)
          elif task[1].replace('entity=', '') in line and 'task=' in task[2]:  # pages ..."entity2" (influence) TODO občas out of index
            array.append(tmp)
      page = line
      pageTitle = line

    elif len(array) > 0:
      if "%%#DOC" not in line and "%%#PAR" not in line:
        page += line

  outputTags = clearPage(page)

###############################################################
# Method for TODO
###############################################################
def extractNames(file, listOfNouns, outputFile, filename, wikiLinksFile):
  print "\033[93mZpracovávám soubor: " + filename + "\033[0m"
  data = ""
  outputTags = ""
  page = ""
  for line in file:
    if "%%#PAGE" in line:
      #wikiLinksFile.write(line)
      # add page link to file
      if len(page) > 0:
        # print page
        page = clearPage(page) + "\n"
        # print page
        # print "###################################################"
        data += persons.getPersons(page, listOfNouns, wikiLinksFile)
        # print data
        # print "###################################################"
        page = ""
      # extract text
      page += line

    elif "%%#DOC" not in line and "%%#PAR" not in line:
      page += line

  page += clearPage(page) + "\n"
  data += persons.getPersons(page, listOfNouns, wikiLinksFile);
  page = ""
  # print data
  outputFile.write(data)
  print "\033[92mSoubor: " + filename + " dokončen.\033[0m"


def createListOfNouns():
  listOfNouns = []
  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/list_of_nouns', 'r')
  for line in file:
    listOfNouns.append(line[:-1])
  return listOfNouns

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  input = sys.argv[1]
  array = []
  outputTags = ""
  pagetitle = ""
  page = ""
  # wikiLinks from each server
  wikiLinksFile = open("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/" + socket.gethostname() + ".links", 'w+')
  # output file with entity
  outputFile = open("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/" + socket.gethostname() + "-non-page.tmp-entity", 'w+')

  listOfNouns = createListOfNouns()
  input_list = find.parseInput(input)  # create input_list
  task_list = find.parseList(input_list)  # create task list

  for filename in glob.glob(os.path.join('/mnt/data/indexes/wikipedia/enwiki-20150901/collPart*', '*.mg4j')):
  #filename = "/mnt/data/indexes/wikipedia/enwiki-20150901/collPart001/athena1_wiki_00.vert.parsed.tagged.mg4j"
  #filename = "/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Andre_Emmerich-knot30-parsed-page.page"
  #filename = "/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Peter_Fuller-knot17-parsed-page.page"
  #if True:
    file = open(filename, 'r')
    # getInformationFromPage(file,task_list)
    extractNames(file, listOfNouns, outputFile, filename,wikiLinksFile)

  task_list = find.setFoundFalse(task_list)
  outputFile.close()

  sys.exit(0)
