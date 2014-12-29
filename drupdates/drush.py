import subprocess
import json
import os
from os.path import expanduser
from drupdates.utils import *

class drush(Settings):

  def __init__(self):
    self.localsettings = Settings()
    aliases = self.localsettings.get('drushAliasFile')

  @property
  def aliases(self):
      return self._aliases
  @aliases.setter
  def aliases(self, value):
    ret = False
    aliasFileName = value
    drushFolder = expanduser('~') + '/.drush'
    drushFile = drushFolder + "/" + aliasFile
    if os.path.isfile(drushFile):
      ret = True
    else:
      if not os.path.isdir(drushFolder):
        try:
          os.makedirs(drushFolder)
          reet = True
        except OSError as e:
          print "Could not create ~/.drush folder \n Error: {0}".format(e.strerror)
      currentDir = os.path.dirname(os.path.realpath(__file__))
      # Symlink the Drush aliases file
      src = currentDir + "/scripts/" + aliasFileName
      try:
        os.symlink(src, drushFile)
        ret = True
      except OSError as e:
        print "Could not create Drush alias file \n Error: {0}".format(e.strerror)
      # Symlink the settings file used by above Drush aliases file
      src = currentDir + "/scripts/settings.py"
      dst = drushFolder + "/settings.py"
      try:
        os.symlink(src, dst)
        ret = True
      except OSError as e:
        print "Could not create settings.py file \n Error: {0}".format(e.strerror)
    self._aliases = ret


  def readUpdateReport(self, lst, updates = []):
    for x in lst:
      # build list of updates in a list,
      # when you hit a blank line you are done
      # note: if there are no updates the first line will be blank
      if not x == '':
        updates += x
      else:
        break

    return updates

  def call(self, commands, alias = '', jsonRet = False):
    """ Run a drush comand and return a list/dictionary of the results

    Keyword arguments:
    commands -- list containing command, arguments and options
    alias -- drush site alias of site where "commands" to run on
    json -- binary deermining if the given command can/should return json

    """
    # https://github.com/dsnopek/python-drush/, threw errors calling Drush()
    # consider --strict=no
    if not alias == '':
      commands.insert(0, '@' + alias)
    if jsonRet:
      commands.append('--format=json')
    commands.insert(0, 'drush')
    # run the command
    popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if jsonRet:
      try:
        ret = json.loads(stdout)
      except ValueError:
        ret =  "No JSON returned for status, though it was requested"
    else:
      ret = stdout.split('\n')
    return ret

  def importDrush(self, alias):
    """ Import a SQL dump using drush sqlc

    alias -- A Drush alias

    """
    workingDir = self.localsettings.get('workingDir')
    backportDir = workingDir + self.localsettings.get('backupDir')
    commands = ['drush', '@' + alias, 'sqlc']
    popen = subprocess.Popen(commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    out, stderr = popen.communicate(file(backportDir + alias + '.sql').read())
    if not stderr == '':
      print alias + " DB import error: " + stderr
      return False

    return True


