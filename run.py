#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

###############################################################
# Imports
###############################################################
import sys  # stdin, stdout, stderr
import os
import subprocess
import argparse
import glob
import os.path
import re

# Vlastní importy
from src import extractRedirects
from src import fillElastic
from src import checkElastic
from src import config


###############################################################
# Constants
###############################################################
PATHPREFIX = config.CONF['path']
TRUE = 'True'
FALSE = 'False'

###############################################################
# Class for terminal colors
###############################################################
class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

###############################################################
# Method for parse input
###############################################################
def parseInput(tmp_input):
  str = raw_input("Enter your input (for more information start program with -h: ")
  print str
  # create file with input from user
  f = open(tmp_input, 'wb')
  f.write(str)
  f.close

###############################################################
# Method for complete all found links into one file
###############################################################
def concatUrlFiles():
  lineCounter = 0
  with open(PATHPREFIX+ 'Wikilinks/all-wiki-links.articles', 'w+') as outfile:
     for filename in glob.glob(os.path.join(PATHPREFIX+ 'Wikilinks/', '*.links')):
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  print bcolors.WARNING + "Mažu pomocné soubory..." + bcolors.ENDC
  # clearing *.tmp files
  for file in glob.glob(PATHPREFIX+ 'Wikilinks/*.links'):
    os.remove(file)
  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet nalezených stránek: {}".format(lineCounter) + bcolors.ENDC

###############################################################
# Method for concat files with entity
###############################################################
def concatFiles():
  lineCounter = 0

  with open(PATHPREFIX+ 'ExtractedEntity/entity-non-page.check', 'w+') as outfile:
   for filename in glob.glob(os.path.join(PATHPREFIX+ 'ExtractedEntity', '*.entity')):
     with open(filename) as infile:
       for line in infile:
         lineCounter += 1
         outfile.write(line)
  outfile.close()
  for file in glob.glob(PATHPREFIX+ 'ExtractedEntity/*.entity'):
    os.remove(file)

  with open(PATHPREFIX+ 'Statistic/statistic.stats', 'w+') as outfile:
   for filename in glob.glob(os.path.join(PATHPREFIX+ 'Statistic', '*.tmp-stats')):
     with open(filename) as infile:
       for line in infile:
         outfile.write(line)
  outfile.close()
  for file in glob.glob(PATHPREFIX+ 'Statistic/*.tmp-stats'):
    os.remove(file)


  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet nalezených entit bez článku: {}".format(lineCounter) + bcolors.ENDC

###############################################################
# Method for split big entity file to cluster
###############################################################
def splitCheckedEntity(servers):
  entityCounter = 0
  cnt = 0
  fileNames = []
  x = 0

  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server)
      if serverName:
        fileNames.append(serverName.group(1))

  with open(PATHPREFIX+ 'CheckedLinks/entity-non-page.checkedv2', 'r') as entityFile:
    for line in entityFile:
      entityCounter += 1

    fileSize = entityCounter / 31 + 2000

  # TODO - nastavit správný vstup
  with open(PATHPREFIX+'CheckedLinks/entity-non-page.checkedv2', 'r') as entityFile:
    clusterFile = open(PATHPREFIX + 'FinalInformation/' + fileNames[x] + '-extracted.info', 'w+')
    for line in entityFile:
      clusterFile.write(line)
      cnt += 1
      if cnt == fileSize:
        cnt = 0
        clusterFile.close()
        x += 1
        clusterFile = open(PATHPREFIX + 'FinalInformation/' + fileNames[x] + '-extracted.info', 'w+')
    clusterFile.close()

###############################################################
# Method for join final files
###############################################################
def reJoinInfoFiles():
  # joining final files
  with open(PATHPREFIX+'FinalInformation/entity-non-page.extracted', 'w+') as outputFile:
    for filename in glob.glob(os.path.join(PATHPREFIX+ 'FinalInformation/', '*.info-extracted')):
      with open(filename) as infile:
        for line in infile:
          outputFile.write(line)
  outputFile.close()
  for file in glob.glob(PATHPREFIX+ 'FinalInformation/*.info-extracted'):
    os.remove(file)
  for file in glob.glob(PATHPREFIX+ 'FinalInformation/*.info'):
    os.remove(file)


###############################################################
# Method for check create subfolders
###############################################################
def createFolders():
  if not os.path.exists(PATHPREFIX+ 'ExtractedEntity'):
    print ("Vytvářím složku: ExtractedEntity")
    os.makedirs(PATHPREFIX + 'ExtractedEntity')
  if not os.path.exists(PATHPREFIX+ 'Wikilinks'):
    print ("Vytvářím složku: Wikilinks")
    os.makedirs(PATHPREFIX + 'Wikilinks')
  if not os.path.exists(PATHPREFIX+ 'CheckedLinks'):
    print ("Vytvářím složku: CheckedLinks")
    os.makedirs(PATHPREFIX + 'CheckedLinks')
  if not os.path.exists(PATHPREFIX+ 'Deleted'):
    print ("Vytvářím složku: Deleted")
    os.makedirs(PATHPREFIX + 'Deleted')
  if not os.path.exists(PATHPREFIX+ 'Statistic'):
    print ("Vytvářím složku: Statistic")
    os.makedirs(PATHPREFIX + 'Statistic')
  if not os.path.exists(PATHPREFIX+ 'FinalInformation'):
    print ("Vytvářím složku: FinalInformation")
    os.makedirs(PATHPREFIX + 'FinalInformation')

###############################################################
# Method for check exists files (already extracted entity with system)
###############################################################
def checkExtractedData(servers):
  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server).group(1)
      if not os.path.exists(PATHPREFIX+ 'ExtractedEntity/'+serverName+ '-non-page.entity'):
        return False
  return True

###############################################################
# Method for check exists files (already checked with system)
###############################################################
def checkCheckedData(servers):
  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server).group(1)
      if not os.path.exists(PATHPREFIX+ 'CheckedLinks/'+serverName+ '.checked'):
        return False
  return True

###############################################################
# Method for parse arguments from config file and terminal
###############################################################
def parseArguments(results):
  global PATHPREFIX
  if results.path:
    PATHPREFIX = results.path
  if not results.servers:
    results.servers = config.CONF['hosts']
  if not results.force:
    results.force = config.CONF['force']
  if not results.update:
    results.update = config.CONF['update']
  if not results.redirects:
    results.redirects = config.CONF['redirects']
  if not results.check:
    results.check = config.CONF['checkUrl']

  return results

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  # parse arguments
  parser = argparse.ArgumentParser(description='Wiki extractor argument parser')
  requiredArguments = parser.add_argument_group('required arguments')
  #requiredArguments.add_argument('-s', '--servers', action="store", dest="servers", help='Add path to server list', required=True)
  optionalArguments = parser.add_argument_group('optional arguments')
  parser.add_argument('-s', '--servers', action="store", dest="servers", help='Add path to server list')
  parser.add_argument('-f', '--force', action="store", dest="force", help='Re-write all extracted data by force')
  parser.add_argument('-r', '--redirects', action="store", dest="redirects", help='System will extract redirect links')
  parser.add_argument('-ch', '--check', action="store", dest="check", help='System will check extracted entity articles')
  parser.add_argument('-p', '--path', action="store", dest="path", help='Path prefix for extraction data')
  parser.add_argument('-u', '--update', action="store", dest="update", help='System will update database with extracted links')
  results = parser.parse_args()

  results = parseArguments(results)
  print results
  print os.getcwd()

  # connect to servers
  try:
    createFolders()  # create folders

    # Entity extract
    if not os.path.exists(PATHPREFIX+ 'ExtractedEntity/entity-non-page.check') or results.force is TRUE:
      print bcolors.WARNING + "Spouštím extrakci entit..."+bcolors.ENDC
      #subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python "+os.getcwd()+"/extract.py "+PATHPREFIX,shell=True)
      print bcolors.OKGREEN + "Dokončena extrakce entit!"+bcolors.ENDC

    # Wikilinks concatenate
    if not os.path.exists(PATHPREFIX+ 'Wikilinks/all-wiki-links.articles') or results.force is TRUE:
      print bcolors.OKGREEN + "Spouštím tvorbu URL souboru..." + bcolors.ENDC
      #concatUrlFiles()

    # Redirects extract
    if not os.path.exists(PATHPREFIX+ 'Wikilinks/redirectedLinks.redirect') or results.force is TRUE or results.redirects is TRUE:
      print bcolors.OKGREEN + "Spouštím extrakci přesměrovaných odkazů..." + bcolors.ENDC
      #extractRedirects.findRedirects(PATHPREFIX)

    # Concat entity file
    if not os.path.exists(PATHPREFIX+ 'ExtractedEntity/entity-non-page.check') or results.force is TRUE:
      print bcolors.OKGREEN + "Spouštím tvorbu souboru s entitami..." + bcolors.ENDC
      #concatFiles()

    # Update elastic
    if results.force is TRUE or results.update is TRUE:
      print bcolors.OKGREEN + "Spouštím update databáze..." + bcolors.ENDC
      #fillElastic.insertData(PATHPREFIX)'''

    # Check entity url
    if not os.path.exists(PATHPREFIX+'CheckedLinks/entity-non-page.checked') or results.force is TRUE or results.check is TRUE:
      print bcolors.WARNING + "Spouštím kontrolu odkazů..."+bcolors.ENDC
      #checkElastic.checkURL(PATHPREFIX)
      print bcolors.OKGREEN + "Kontrola dokončena."+bcolors.ENDC

    # Extract information
    if not os.path.exists(PATHPREFIX+'FinalInformation/entity-non-page.info') or results.force is TRUE:
      print bcolors.WARNING + "Spouštím extrakci informací..."+bcolors.ENDC
      #splitCheckedEntity(results.servers)
      print bcolors.WARNING + "Rozděleny soubory, spuštím samotnou extrakci..."+bcolors.ENDC
      #subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python "+os.getcwd()+"/retreiveInfo.py "+PATHPREFIX+",shell=True)
      print bcolors.WARNING + "Spojuji soubory..."+bcolors.ENDC
      #reJoinInfoFiles()
      print bcolors.OKGREEN + "Extrakce informací dokončena!"+bcolors.ENDC

  except OSError as e:
    print bcolors.FAIL + "Execution failed:" + bcolors.ENDC + "", e

  sys.exit(0)

# KILL-ALL -> parallel-ssh -t 0 -i -h servers.txt -A pkill -u xstejs24