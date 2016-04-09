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

def concatUrlFiles():
  nameArray = {}
  previousLine = ""
  addLine = ""
  lineCounter = 0
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/all-wiki-links.aux', 'w+') as outfile:
     for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/', '*.links')):
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  print bcolors.WARNING + "Mažu pomocné soubory..." + bcolors.ENDC
  # clearing *.tmp files
  for file in glob.glob("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/*.links"):
    os.remove(file)
  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet nalezených stránek: {}".format(lineCounter) + bcolors.ENDC

###############################################################
# Method for concat files with entity
###############################################################
def concatFiles():
  nameArray = {}
  lineCounter = 0
  # entities without page (not-checked redirect yet)
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/entity-non-page.none', 'w+') as outfile:
     for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/', '*.checked')): #TODO - file *.checked !!!
       print filename
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  # delete entites -> they already have page (only or testing now)
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/entity-non-page.del', 'w+') as outfile:
     for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/', '*.deleted')):
       print filename
       with open(filename) as infile:
         for line in infile:
           lineCounter += 1
           outfile.write(line)
  outfile.close()
  print bcolors.WARNING + "Mažu pomocné soubory..." + bcolors.ENDC
  # clearing *.tmp files
  for file in glob.glob("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/*.checked"):
    os.remove(file)
  for file in glob.glob("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/*.deleted"):
    os.remove(file)
  print bcolors.OKGREEN + "Soubor vytvořen!" + bcolors.ENDC
  print bcolors.OKGREEN + "Počet řádků: {}".format(lineCounter) + bcolors.ENDC

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  tmp_input = "/mnt/minerva1/nlp/projects/ie_from_wikipedia7/input.tmp"
  # parse arguments
  parser = argparse.ArgumentParser(description='Wiki extractor argument parser')
  requiredArguments = parser.add_argument_group('required arguments')
  requiredArguments.add_argument('-s', '--servers', action="store", dest="servers", help='Add path to server list', required=True)
  parser.add_argument('-i', '--input', action="store", dest="input", help='Input file with information for verify')
  results = parser.parse_args()

  # parse
  if results.input is None:
    parseInput(tmp_input)
    results.input = tmp_input

  # connect to servers
  try:
    if subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/extract.py " + results.input,shell=True) == 0:
      print bcolors.OKGREEN + "Dokončena extrakce!" + bcolors.ENDC + bcolors.OKGREEN + "Spouštím tvorbu URL souboru..." + bcolors.ENDC
      concatUrlFiles()
      print bcolors.OKGREEN + "Done" + bcolors.ENDC
      #sys.exit(0)
    else:
      print bcolors.FAIL + "Chyba na některém serveru" + bcolors.ENDC
      #sys.exit(1)
    print bcolors.OKGREEN + "Spouštím ověřování URL..." + bcolors.ENDC
    if subprocess.call("parallel-ssh -t 0 -i -h " + results.servers + " -A python3 /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/check-url.py ",shell=True) == 0:
      print bcolors.OKGREEN + "Dokončena kontrola URL!" + bcolors.ENDC + bcolors.OKGREEN + "Spouštím tvorbu výsledného souboru..." + bcolors.ENDC
      concatFiles()
      print bcolors.OKGREEN + "Done" + bcolors.ENDC
      sys.exit(0)
    else:
      print bcolors.FAIL + "Chyba na některém serveru" + bcolors.ENDC
      sys.exit(1)
  except OSError as e:
    print bcolors.FAIL + "Execution failed:" + bcolors.ENDC + "", e

  sys.exit(0)