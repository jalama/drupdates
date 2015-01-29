import subprocess
import json
import os
from os.path import expanduser
from drupdates.utils import *

class drush(Settings):

  def __init__(self):
    self.settings = Settings()

  def readUpdateReport(self, lst, updates = []):
    """ Read the report produced the the Drush pm-update command."""
    updates = []
    for x in lst:
      # build list of updates, when you hit a blank line you are done
      # note: if there are no updates the first line will be blank
      if x:
        updates.append(x)
      else:
        break
    return updates

  def call(self, commands, alias = '', jsonRet = False):
    """ Run a drush comand and return a list/dictionary of the results.

    Keyword arguments:
    commands -- list containing command, arguments and options
    alias -- drush site alias of site where "commands" to run on
    json -- binary deermining if the given command can/should return json

    """
    # FIXME: Allow commands ro be run on all drupdates sites at one time
    # ie drush @drupdates <some command>
    # https://github.com/dsnopek/python-drush/, threw errors calling Drush()
    if alias:
      commands.insert(0, '@drupdates.' + alias)
    if jsonRet:
      commands.append('--format=json')
    commands.insert(0, 'drush')
    # run the command
    try:
      popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
      print "Cannot run drush.call(), most likely because python can't find drush\n Error: {0}".format(e.strerror)
    stdout, stderr = popen.communicate()
    if jsonRet:
      try:
        ret = json.loads(stdout)
      except ValueError:
        ret =  "For {0}, No JSON returned for status, though it was requested".format(alias)
    else:
      ret = stdout.split('\n')
    return ret

  def dbImport(self, alias):
    """ Import a SQL dump using drush sqlc.

    alias -- A Drush alias

    """
    workingDir = self.settings.get('workingDir')
    backportDir = self.settings.get('backupDir')
    if os.path.isfile(backportDir + alias + '.sql'):
      commands = ['drush', '@drupdates.' + alias, 'sqlc']
      popen = subprocess.Popen(commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
      out, stderr = popen.communicate(file(backportDir + alias + '.sql').read())
      if stderr:
        print "{0} DB import error: {1}".format(alias, stderr)
        return False
    else:
      print "{0} could not find backup file".format(alias)
      return False
    return True




