#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import subprocess
import argparse
import re


# Function for find some information from user in text
def checkInformation(outputTags, find, task_list):
  tmp_array = []
  tmp_array = list(find)
  print outputTags

  outputTags = outputTags.split('\n')
  print outputTags[0]
  for line in outputTags:
    find = list(tmp_array)
    for task in find:
      tmp = task
      if re.search('.*task=influence', task):
        # print "influence"
        task = task.split('|')
        task[0] = task[0].replace('entity=', '')
        task[1] = task[1].replace('entity=', '')
        # task[3] obsahuje původní otázku
        if re.search(task[0].replace(' ', '.*'), line) and re.search(task[1].replace(' ', '.*'),line):  # both entities are in one sentence
          print "Oboje ve větě"
          tmp_array.remove(tmp)
          task_list[task_list.index(tmp)] = task[3] + " -> True"
        # print line
        elif re.search(task[0].replace(' ', '.*'), line) and re.search('she|he', line,re.I):  # co-reference by she/he in case of first entity
          # print "Pouze prvni entita, druhá odkazuje pomocí he/she"
          # najít verb (V..) v tagu a vyhodnotit ovlivnění, vyhodnotit he/she
          tmp_array.remove(tmp)
        elif re.search(task[1].replace(' ', '.*'), line) and re.search('she|he', line,re.I):  # co-reference by she/he in case of second entity
          # print "Pouze druha entita, druhá odkazuje pomocí he/she"
          # najít verb (V..) v tagu a vyhodnotit ovlivnění, vyhodnotit he/she
          tmp_array.remove(tmp)

      elif re.search('.*verb=', task):
        # print "verb"
        task = task.split('|')
        task[0] = task[0].replace('entity=', '')
        task[1] = task[1].replace('verb=', '')
        task[2] = task[2].replace('rest=', '')
        # task[3] obsahuje původní otázku
        # TODO - zda se mi, že to vyhodnocuje mockrát
        # print '('+task[0].replace(' ','.*')+').*\['+task[1]+'.*'+task[2].replace(' ','.*')+'[^\\n.?!]+'
        # print line
        # print '('+task[0].replace(' ','.*')+').*'+task[1]+'.*'+task[2]+'[^\\n.?!]+' - hledající regex
        if re.search('pronoun=', task[2]):
          task[2] = task[2].replace('pronoun=', '')
          # print task[3]
          # print '('+task[0].replace(' ','.*')+').*\['+task[1]
          # print line
          answer = re.search('(' + task[0].replace(' ', '.*') + ').*\[' + task[1], line)
          if answer:
            line = re.sub(r'\|[^\s]+', '', line)
            task_list[task_list.index(tmp)] = task[3] + " -> Answer: " + re.sub('(\([^\)]+\)\s)', '',line.replace('[[','').replace('\t]]', '')[:-3]) + "."
            tmp_array.remove(tmp)
          elif re.search('(' + task[0].replace(' ', '.*') + ').*', line):
            # print "tyrael"
            # print line
            answer = re.search('(\[([^\|]+)\|V[^\|]+\|([^\]]+)\])', line)
            if answer and re.search('is|was|will|were|are', task[1]) and answer.group(3) == 'be':
              # print "mephisto"
              # print line
              # print line
              line = re.sub(r'\|[^\s]+', '', line)
              task_list[task_list.index(tmp)] = task[3] + " -> Answer: " + re.sub('(\([^\)]+\)\s)', '',line.replace('[[','').replace('\t]]', '')[:-3]) + "."
              tmp_array.remove(tmp)
        # hledání vět typu - Einstein is
        elif re.search('(' + task[0].replace(' ', '.*') + ').*\[' + task[1] + '.*' + task[2].replace(' ','.*') + '[^\n.?!]+',
                       line):
          tmp_array.remove(tmp)
          # print '('+task[0].replace(' ','.*')+').*\['+task[1]+'.*'+task[2].replace(' ','.*')+'[^\n.?!]+'
          task_list[task_list.index(tmp)] = task[3] + " -> True"
          # pomocný výpis
          # print task[3] + " -> True"
        elif re.search('(' + task[0].replace(' ', '.*') + ').*', line):
          # opravování slovesného času is/was atd.
          verb = re.search('(\[([^\|]+)\|V[^\|]+\|([^\]]+)\])', line)
          if verb:
            if re.search('is|was|will|were|are', task[1]) and verb.group(3) == 'be':
              line = re.sub(r'\|[^\s]+', '', line)
              task_list[task_list.index(tmp)] = task[3] + " -> False: " + re.sub('(\([^\)]+\)\s)', '',line.replace('[[','').replace('\t]]', '')[:-3]) + "."
              tmp_array.remove(tmp)
              # pomocný výpis TODO - POZOR!!! nastaveno mazání informací v závorce!!! (\([^\)]+\)\s)
              # print task[3] + " -> False: "+re.sub('(\([^\)]+\)\s)','',line.replace('[[','').replace('\t]]','')[:-3])+"."

  return task_list


# Function for find some information from user in text (not Influence and List pages)
def checkInfluencePages(outputTags, find, task_list):
  tmp_array = []
  tmp_array = list(find)
  print "Parse influence page"
  print outputTags

  outputTags = outputTags.split('\n')
  print outputTags[0]
  for line in outputTags:
    find = list(tmp_array)
    for task in find:
      tmp = task
      if re.search('.*task=influence', task):
        # print "influence"
        task = task.split('|')
        task[0] = task[0].replace('entity=', '')
        task[1] = task[1].replace('entity=', '')
        # task[3] obsahuje původní otázku
        if re.search(task[0].replace(' ', '.*'), line) and re.search(task[1].replace(' ', '.*'),line):  # both entities are in one sentence
          tmp_array.remove(tmp)
          task_list[task_list.index(tmp)] = task[3] + " -> True"
        elif re.search(task[1].replace(' ', '.*'), line) and (
              re.search('she|he', line, re.I) or re.search(task[0], outputTags[0])):  # co-reference by she/he in case of second entity
          # print "Pouze druha entita, druhá odkazuje pomocí he/she"
          # najít verb (V..) v tagu a vyhodnotit ovlivnění, vyhodnotit he/she
          tmp_array.remove(tmp)
          task_list[task_list.index(tmp)] = task[3] + " -> True"

  return task_list


# Function for finding relation ship between entities
def findRealitonship(line):
  print "test"


# Function for "which" information we need to find
def parseList(input_list):
  # TODO - možná další případy
  task_list = []
  for line in input_list:
    finding = re.search('((.*) - (.*))|([A-Z].*[^\n])|([A-Z].*)', line)
    # case of personA - personB format  (B is unfluenced by A)
    if finding:
      if finding.group(3):
        # for page regex
        task_list.append(
          "entity=" + finding.group(2) + "|entity=" + finding.group(3) + "|task=influence|" + line)
      # caseof sentence (Einstein is...)
      else:
        finding = re.search('(W[^\s]+)\s+([^\s]+)\s+([^?.!\n\0]+)', line)
        '''Who is Mozart, What is Hollywood, Where is Colorado, When ends Wolrd War 2'''
        if finding:
          task_list.append("entity=" + finding.group(3) + "|verb=" + finding.group(2) + "|pronoun=" + finding.group(1) + "|" + line)
        '''"Albert Einstein" was physicist, "Anderson" is actor, "Barack Obama" is president'''
        finding = re.search('"(.*)"\s+([^\s]+)\s+([^?.!\n\0]+)', line)
        if finding:
          task_list.append("entity=" + finding.group(1) + "|verb=" + finding.group(2) + "|rest=" + finding.group(3) + "|" + line)

  # print task_list
  return task_list


# Function for parse urser's input
def parseInput(file):
  input_list = []
  f = open(file, 'r')
  if re.search('.*/input.tmp', file):  # delete tmp file
    for line in f:
      input_list = line.split('|')
    f.close
    os.remove(file)
  else:
    for line in f:
      input_list.append(line.replace('\n', ''))
      f.close
  # print input_list
  return input_list


# Function for parse task - TODO - může se smazat
def parseTask(task, line, find):
  tmp = task
  if re.search('.*(task=influence)', task):  # influence task- list of persons....
    task = task.split('|')
    first_page = re.search('entity=([^\s]+).*\s([^\|]+)', task[0])
    second_page = re.search('entity=([^\s]+).*\s([^\|]+)', task[1])
    if first_page:
      if re.search(first_page.group(1), line) and re.search(first_page.group(2), line):
        if tmp not in find:
          find.append(tmp)
    if second_page:
      if re.search(second_page.group(1), line) and re.search(second_page.group(2), line):
        if tmp not in find:
          find.append(tmp)
  elif re.search('.*pronoun=W.*', task):  # pronoun task
    task = task.split('|')
    page = re.search('entity=([^\s]+).*\s([^\|]+)', task[0])
    if page:
      if re.search(page.group(1), line) and re.search(page.group(2), line):
        if tmp not in find:
          find.append(tmp)
  elif re.search('.*verb=.*', task):  # clasic task
    task = task.split('|')
    page = re.search('entity=([^\s]+).*\s([^\|]+)', task[0])
    if page:
      if re.search(page.group(1), line) and re.search(page.group(2), line):
        if tmp not in find:
          find.append(tmp)

  return find


# Function for set false for all not-found results
def setFoundFalse(task_list):
  for task in task_list:
    tmp = task
    if not "->" in task:
      task = task.split('|')
      task_list[task_list.index(tmp)] = task[3] + " -> Not Found"
  return task_list
