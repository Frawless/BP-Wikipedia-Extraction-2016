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
import time

# import of created modules
import find
import persons

###############################################################
# Extractor class
###############################################################
class Extract:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
    self.PathPerfix = sys.argv[1]
    self.wikiLinks = open(self.PathPrefix+'Wikilinks/' + socket.gethostname() + '.links', 'w+')
    self.outputFile = open(self.PathPrefix+'ExtractedEntity/' + socket.gethostname() + '-non-page.entity', 'w+')
    self.listOfNouns = self.createListOfNouns()
    self.pageURLs = []
    # Extraction statistics
    self.startTime = time.time()
    self.executionTime = 0
    self.host = socket.gethostname()
    self.articlesCount = 0
    self.extractedEntityCount = 0

  ###############################################################
  # Method for clear page
  ###############################################################
  def clearPage(self, page):
    self.pageURLs = []
    pageTag = False
    parsedPage = ""
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

      if "%%#SEN" in line:
        parsedPage += "\n"
        pageTag = False
        continue

      if not pageTag:
        tmp = re.search(r'^\d+\s+([^\s]+\s+[^\s]+\s+[^\s]+)',line)  # token + tag + lemma - can be modifed for another options
        tmpNertag = re.search(r'\d+\s+([^\s]+\s+){14}', line)  # LF nertag
        tmpURL = re.search(r'\d+\s+([^\s]+\s+){9}', line)  # changd from 9 to 15 ?!!!
        if not tmpURL:
          tmpURL = re.search(r'\d+\s+([^\s]+\s+){15}', line)

        pageURLs = re.search(r'\d+\s+([^\s]+\s+){15}', line)
        if pageURLs:
          if not re.search('0',pageURLs.group(1)):
            self.pageURLs.append(pageURLs.group(1).replace('http://en.wikipedia.org/wiki/','').replace('_',' ').replace('\t',''))

        if tmpNertag and tmp and tmpURL:
          if "0" not in tmpNertag.group(1) and "0" not in tmpURL.group(1):
            parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|entity=" + tmpNertag.group(1)[:-1] + "|URL=" + tmpURL.group(1)[:-1] + "]] "
          elif "0" in tmpNertag.group(1) and "0" not in tmpURL.group(1):
            parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|URL=" + tmpURL.group(1)[:-1] + "]] "
          elif "0" not in tmpNertag.group(1) and "0" in tmpURL.group(1):
            parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "|entity=" + tmpNertag.group(1)[:-1] + "]] "
          else:
            parsedPage += "[[" + re.sub('\s+', '|', tmp.group(1)) + "]] "
    return parsedPage

  ###############################################################
  # Method for extract single entity
  ###############################################################
  def extractNames(self, file):
    data = ""
    person = persons.PersonClass(self.wikiLinks, self.listOfNouns)
    page = ""
    for line in file:
      if "%%#PAGE" in line:
        # add page link to file
        if len(page) > 0:
          ###############################################################
          page = self.clearPage(page) + "\n"
          data += person.getPersons(page, self)
          ###############################################################
          page = ""
        # extract text
        page += line
      elif "%%#DOC" not in line and "%%#PAR" not in line:
        page += line
    ###############################################################
    page += self.clearPage(page) + "\n"
    data += person.getPersons(page,self)
    ###############################################################
    page = ""
    self.outputFile.write(data)

  ###############################################################
  # Method for collect most using nouns
  ###############################################################
  def createListOfNouns(self):
    listOfNouns = []
    file = open(self.PathPerfix+'/list_of_nouns', 'r')
    for line in file:
      listOfNouns.append(line[:-1])
    return listOfNouns

  ###############################################################
  # Method for QA (only for future work)
  ###############################################################
  def getInformationFromPage(self, file, task_list):
    for line in file:
      if "%%#PAGE" in line:
        # extract text
        if len(array) > 0:
          outputTags = self.clearPage(page)
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
          if "->" not in tmp:
            if 'PAGE ' + task[0].replace('entity=', '') + '\thttp' in line and 'verb=' in task[1]:  # pages "entity"
              array.append(tmp)
            elif task[0].replace('entity=', '') in line and 'verb=' not in task[1]:  # pages ..."entity"
              array.append(tmp)
            elif task[0].replace('entity=', '') in line and 'task=' in task[2]:  # pages ..."entity1" (influence)
              array.append(tmp)
            elif task[1].replace('entity=', '') in line and 'task=' in task[2]:  # pages ..."entity2" (influence)
              array.append(tmp)
        page = line
        pageTitle = line

      elif len(array) > 0:
        if "%%#DOC" not in line and "%%#PAR" not in line:
          page += line

  ###############################################################
  # Method for print server extract stats
  ###############################################################
  def showStats(self):
    with open(self.PathPrefix+'/Statistic/statistic'+self.host+'.tmp-stats', 'w+') as statsFile:
      statsFile.write('###############################################################\n')
      statsFile.write('# Server:\t'+self.host+'\n')
      statsFile.write('# Execution time:\t'+str(self.executionTime)+' min\n')
      statsFile.write('# Parsed Articles:\t'+str(self.articlesCount)+'\n')
      statsFile.write('# Extracted Entity:\t'+str(self.extractedEntityCount)+'\n')
      statsFile.write('###############################################################\n\n')

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  array = []
  outputTags = ""
  pagetitle = ""
  page = ""
  id = 0
  extractor = Extract()

  for filename in glob.glob(os.path.join('/mnt/data/indexes/wikipedia/enwiki-20150901/collPart*', '*.mg4j')):
    file = open(filename, 'r')

  #with open(PATHPREFIX+'Origins_of_the_American_Civil_War-athena5-parsed-page.page') as file:
    # getInformationFromPage(file,task_list)
    extractor.extractNames(file)

  extractor.wikiLinks.close()
  extractor.outputFile.close()
  extractor.executionTime = (time.time() - extractor.startTime) / 60  # Exec time in minutes
  extractor.showStats()  # Show Stats


  sys.exit(0)
