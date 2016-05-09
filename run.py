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

  '''for filename in glob.glob(os.path.join(PathPrefix+'ExtractedEntity', '*.entity')):
    with open(filename) as infile:
      for line in infile:
        lineCounter += 1'''

  with open(PathPrefix+'ExtractedEntity/entity-non-page.checkv2', 'w+') as outfile:
   for filename in glob.glob(os.path.join(PathPrefix+'ExtractedEntity', '*.entity')):
     with open(filename) as infile:
       for line in infile:
         lineCounter += 1
         outfile.write(line)
  outfile.close()
  '''for file in glob.glob(PathPrefix+'ExtractedEntity/*.entity'):
    os.remove(file)'''

  # entities without page (not-checked redirect yet)
  '''with open(PathPrefix+'entity-non-page.none', 'w+') as outfile:
     for filename in glob.glob(os.path.join(PathPrefix+'CheckedLinks', '*.checked')):
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  # delete entites -> they already have page (only or testing now)
  with open(PathPrefix+'entity-non-page.del', 'w+') as outfile:
     for filename in glob.glob(os.path.join(PathPrefix+'Deleted/', '*.deleted')):
       with open(filename) as infile:
         for line in infile:
           outfile.write(line)
  outfile.close()
  print bcolors.WARNING + "Mažu pomocné soubory..." + bcolors.ENDC
  # clearing *.tmp files
  for file in glob.glob(PathPrefix+'CheckedLinks/*.checked'):
    os.remove(file)
  for file in glob.glob(PathPrefix+'Deleted/*.deleted'):
    os.remove(file)'''
  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet nalezených entit bez článku: {}".format(lineCounter) + bcolors.ENDC

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

###############################################################
# Method for check exists files (already extracted entity with system)
###############################################################
def checkExtractedData(servers):
  return True
  with open (servers) as serversFile:
    for server in serversFile:
      serverName = re.search('([^\.]+)\.fit\.vutbr\.cz',server).group(1)
      if not os.path.exists(PathPrefix+'ExtractedEntity/'+serverName+'-non-page.entity'):
        return False
  return True

###############################################################
# Method for check exists files (already checked with system)
# TODO - delete
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
  parser.add_argument('-a', '--allentity', action="store_true", help='System will extract all entity from input')
  results = parser.parse_args()

  # connect to servers
  try:
    createFolders()  # create folders
    if os.path.exists(PathPrefix+'statistic.stats'):
      os.remove(PathPrefix+'statistic.stats')  # remove old statistic file

    if not os.path.exists(PathPrefix+'ExtractedEntity/entity-non-page.check') or results.force:
      print bcolors.WARNING + "Spouštím extrakci..."+bcolors.ENDC
      subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/extract.py ",shell=True)
      print bcolors.OKGREEN + "Dokončena extrakce!"+bcolors.ENDC

    '''if not os.path.exists(PathPrefix+'Wikilinks/all-wiki-links.aux') or results.force:
      print bcolors.OKGREEN + "Spouštím tvorbu URL souboru..." + bcolors.ENDC
      concatUrlFiles()'''

    if not os.path.exists(PathPrefix+'ExtractedEntity/entity-non-page.check') or results.force:
      print bcolors.OKGREEN + "Spouštím tvorbu souboru s entitami..." + bcolors.ENDC
      concatFiles()

    '''if not os.path.exists(PathPrefix+'CheckedLinks/entity-non-page.checked') or results.force:
      print bcolors.WARNING + "Spouštím kontrolu odkazů..."+bcolors.ENDC
      checkElastic.checkURL()
      print bcolors.OKGREEN + "Kontrola dokončena."+bcolors.ENDC'''

    # TODO - backup - původní verze
    '''if not checkCheckedData(results.servers) or results.force:
      print bcolors.WARNING + "Spouštím kontrolu odkazů..."+bcolors.ENDC
      subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python3 /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/check-url.py ",shell=True)
      print bcolors.OKGREEN + "Dokončena kontrola URL!" + bcolors.ENDC + bcolors.OKGREEN + "Spouštím tvorbu výsledného souboru..." + bcolors.ENDC
      concatFiles()'''

  except OSError as e:
    print bcolors.FAIL + "Execution failed:" + bcolors.ENDC + "", e

  sys.exit(0)

# KILL-ALL -> parallel-ssh -t 0 -i -h servers.txt -A pkill -u xstejs24