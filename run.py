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

# mine imports
from src import retreiveInfo
from src import extractRedirects
from src import fillElastic
from src import checkElastic

###############################################################
# Constants
###############################################################
PathPrefix = '/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'

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
  with open(PathPrefix+'Wikilinks/all-wiki-links.aux', 'w+') as outfile:
     for filename in glob.glob(os.path.join(PathPrefix+'Wikilinks/', '*.links')):
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  print bcolors.WARNING + "Mažu pomocné soubory..." + bcolors.ENDC
  # clearing *.tmp files
  for file in glob.glob(PathPrefix+'Wikilinks/*.links'):
    os.remove(file)
  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet nalezených stránek: {}".format(lineCounter) + bcolors.ENDC

###############################################################
# Method for concat files with entity
###############################################################
def concatFiles():
  lineCounter = 0

  with open(PathPrefix+'ExtractedEntity/entity-non-page.check', 'w+') as outfile:
   for filename in glob.glob(os.path.join(PathPrefix+'ExtractedEntity', '*.entity')):
     with open(filename) as infile:
       for line in infile:
         lineCounter += 1
         outfile.write(line)
  outfile.close()
  for file in glob.glob(PathPrefix+'ExtractedEntity/*.entity'):
    os.remove(file)

  with open(PathPrefix+'Statistic/statistic.stats', 'w+') as outfile:
   for filename in glob.glob(os.path.join(PathPrefix+'Statistic', '*.tmp-stats')):
     with open(filename) as infile:
       for line in infile:
         outfile.write(line)
  outfile.close()
  for file in glob.glob(PathPrefix+'Statistic/*.tmp-stats'):
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

  with open(PathPrefix+'CheckedLinks/entity-non-page.checkedv2','r') as entityFile:
    for line in entityFile:
      entityCounter += 1

    fileSize = entityCounter / 31 + 2000

  with open(PathPrefix+'CheckedLinks/entity-non-page.checkedv2','r') as entityFile:
    clusterFile = open(PathPrefix+'FinalInformation/'+fileNames[x]+'-extracted.info','w+')
    for line in entityFile:
      #print line
      clusterFile.write(line)
      cnt += 1
      if cnt == fileSize:
        cnt = 0
        clusterFile.close()
        x += 1
        clusterFile = open(PathPrefix+'FinalInformation/'+fileNames[x]+'-extracted.info','w+')
    clusterFile.close()

###############################################################
# Method for join final files
###############################################################
def reJoinInfoFiles():
  # joining final files
  with open(PathPrefix+'FinalInformation/entity-non-page.info', 'w+') as outputFile:
    for filename in glob.glob(os.path.join(PathPrefix+'FinalInformation/', '*.info-extracted')):
      with open(filename) as infile:
        for line in infile:
          outputFile.write(line)
  outputFile.close()
  for file in glob.glob(PathPrefix+'FinalInformation/*.info-extracted'):
    os.remove(file)


###############################################################
# Method for check create subfolders
###############################################################
def createFolders():
  if not os.path.exists(PathPrefix+'ExtractedEntity'):
    print ("Vytvářím složku: ExtractedEntity")
    os.makedirs(PathPrefix+'ExtractedEntity')
  if not os.path.exists(PathPrefix+'Wikilinks'):
    print ("Vytvářím složku: Wikilinks")
    os.makedirs(PathPrefix+'Wikilinks')
  if not os.path.exists(PathPrefix+'CheckedLinks'):
    print ("Vytvářím složku: CheckedLinks")
    os.makedirs(PathPrefix+'CheckedLinks')
  if not os.path.exists(PathPrefix+'Deleted'):
    print ("Vytvářím složku: Deleted")
    os.makedirs(PathPrefix+'Deleted')
  if not os.path.exists(PathPrefix+'Statistic'):
    print ("Vytvářím složku: Statistic")
    os.makedirs(PathPrefix+'Statistic')
  if not os.path.exists(PathPrefix+'FinalInformation'):
    print ("Vytvářím složku: FinalInformation")
    os.makedirs(PathPrefix+'FinalInformation')

###############################################################
# Method for check exists files (already extracted entity with system)
###############################################################
def checkExtractedData(servers):
  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server).group(1)
      if not os.path.exists(PathPrefix+'ExtractedEntity/'+serverName+'-non-page.entity'):
        return False
  return True

###############################################################
# Method for check exists files (already checked with system)
###############################################################
def checkCheckedData(servers):
  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server).group(1)
      if not os.path.exists(PathPrefix+'CheckedLinks/'+serverName+'.checked'):
        return False
  return True

###############################################################
# Method for start parallel shh and extraction on all machines
###############################################################
def startExtraction(results):
  if not checkExtractedData(results.servers) or results.force:
    print bcolors.WARNING + "Spouštím extrakci..."+bcolors.ENDC
    subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/extract.py ",shell=True)
    print bcolors.OKGREEN + "Dokončena extrakce!"+bcolors.ENDC

  if not os.path.exists(PathPrefix+'Wikilinks/all-wiki-links.aux') or results.force:
    print bcolors.OKGREEN + "Spouštím tvorbu URL souboru..." + bcolors.ENDC
    concatUrlFiles()

  if not checkCheckedData(results.servers) or results.force:
    print bcolors.WARNING + "Spouštím kontrolu odkazů..."+bcolors.ENDC
    subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python3 /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/check-url.py ",shell=True)
    print bcolors.OKGREEN + "Dokončena kontrola URL!" + bcolors.ENDC + bcolors.OKGREEN + "Spouštím tvorbu výsledného souboru..." + bcolors.ENDC
    concatFiles()

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  # parse arguments
  parser = argparse.ArgumentParser(description='Wiki extractor argument parser')
  requiredArguments = parser.add_argument_group('required arguments')
  requiredArguments.add_argument('-s', '--servers', action="store", dest="servers", help='Add path to server list', required=True)
  #parser.add_argument('-i', '--input', action="store", dest="input", help='Input file with information for verify')
  optionalArguments = parser.add_argument_group('optional arguments')
  parser.add_argument('-f', '--force', action="store_true", help='Re-write all extracted data by force')
  parser.add_argument('-e', '--elastic', action="store_true", help='System will ubgrade elastic databse with extracted links')
  results = parser.parse_args()


  # connect to servers
  try:
    # TODO - nastavit správně pro celkový systém!
    createFolders()  # create folders

    # Entity extract
    '''if not os.path.exists(PathPrefix+'ExtractedEntity/entity-non-page.check') or results.force:
      print bcolors.WARNING + "Spouštím extrakci entit..."+bcolors.ENDC
      subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/extract.py ",shell=True)
      print bcolors.OKGREEN + "Dokončena extrakce entit!"+bcolors.ENDC'''

    # Wikilinks concatenate
    '''if not os.path.exists(PathPrefix+'Wikilinks/all-wiki-links.aux') or results.force:
      print bcolors.OKGREEN + "Spouštím tvorbu URL souboru..." + bcolors.ENDC
      concatUrlFiles()'''

    # Redirects extract
    '''if not os.path.exists(PathPrefix+'Wikilinks/redirectedLinks.redirect') or results.force:
      print bcolors.OKGREEN + "Spouštím extrakci přesměrovaných odkazů..." + bcolors.ENDC
      extractRedirects.findRedirects()'''

    # Concat entity file
    '''if not os.path.exists(PathPrefix+'ExtractedEntity/entity-non-page.check') or results.force:
      print bcolors.OKGREEN + "Spouštím tvorbu souboru s entitami..." + bcolors.ENDC
      concatFiles()'''

    # Update elastic
    '''if results.elastic:
      print bcolors.OKGREEN + "Spouštím update databáze..." + bcolors.ENDC
      fillElastic.insertData()'''

    # Check entity url
    '''if not os.path.exists(PathPrefix+'CheckedLinks/entity-non-page.checked') or results.force:
      print bcolors.WARNING + "Spouštím kontrolu odkazů..."+bcolors.ENDC
      checkElastic.checkURL()
      print bcolors.OKGREEN + "Kontrola dokončena."+bcolors.ENDC'''

    # Extract information
    if not os.path.exists(PathPrefix+'FinalInformation/entity-non-page.info') or results.force:
      print bcolors.WARNING + "Spouštím extrakci informací..."+bcolors.ENDC
      splitCheckedEntity(results.servers)
      print bcolors.WARNING + "Rozděleny soubory, spuštím samotnou extrakci..."+bcolors.ENDC
      subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/retreiveInfo.py ",shell=True)
      print bcolors.WARNING + "Spojuji soubory..."+bcolors.ENDC
      reJoinInfoFiles()
      print bcolors.OKGREEN + "Extrakce informací dokončena!"+bcolors.ENDC

  except OSError as e:
    print bcolors.FAIL + "Execution failed:" + bcolors.ENDC + "", e

  sys.exit(0)

# KILL-ALL -> parallel-ssh -t 0 -i -h servers.txt -A pkill -u xstejs24