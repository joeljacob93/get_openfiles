#!/usr/bin/env python2.7
#
# Description : Program calculates the number of open files for each user
#               and process
# Usage       : python ./count.py
#

import os
import logging
import time
import subprocess
import re
import collections

#
# Run an external command and wait for its completion
#
def runcmd(cmd):
   p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#   while True:
#       err = p.stderr.read(1)
#       if err == '' and p.poll() != None:
#           break
#       if err != '':
#           logging.info(out)
   out, err = p.communicate()
   return out,err,p.returncode


#
# Configure logging subsystem
#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("Running lsof command, please be patient ...")
out,err,return_code = runcmd('/usr/sbin/lsof')
if return_code != 0:
   logger.critical('Failed to run lsof command: '+err)
   exit(return_code)

users = ""

logger.info('lsof successfully completed, analyzing its output ...')
for line in out.splitlines():
   line = re.sub(' +',' ',line)
   user = line.split(" ")[2]
   if user != "USER":
      users = users+" "+user
userscount = reduce( lambda d, c: d.update([(c, d.get(c,0)+1)]) or d, users.split(), {})
logger.info("Number of open files for each user :")
for key, value in sorted(userscount.iteritems(), key=lambda (k,v): (v,k)):
   logger.info("   %s: %s" % (key, value))

processes= ""
for line in out.splitlines():
   line = re.sub(' +',' ',line)
   process = line.split(" ")[1]
   if process != "PID":
      processes = processes+" "+process
processescount = reduce( lambda d, c: d.update([(c, d.get(c,0)+1)]) or d, processes.split(), {})
logger.info("Number of open files for each process :")
for key, value in sorted(processescount.iteritems(), key=lambda (k,v): (v,k)):
   logger.info("   %s: %s" % (key, value))


logger.info("Getting system limits ...")
out,err,return_code = runcmd('/bin/grep nofile /etc/security/limits.conf')
if return_code != 0:
   logger.critical('Failed to run grep command: '+err)
   exit(return_code)
for line in out.splitlines():
   if "#" not in line:
      logger.info(line)

logger.info("Getting current user's limits ...")
out,err,return_code = runcmd('ulimit -n')
if return_code != 0:
   logger.critical('Failed to run ulimit command: '+err)
   exit(return_code)
for line in out.splitlines():
   logger.info(line)

