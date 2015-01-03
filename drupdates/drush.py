import subprocess
import json
import os
from os.path import expanduser
from drupdates.utils import *

class drush(Settings):

  def __init__(self):
    self.localsettings = Settings()
    self.aliases = self.localsettings.get('drushAliasFile')

  @property
  def aliases(self):
      return self._aliases
  @aliases.setter
  def aliases(self, value):
    ret = False
    aliasFileName = value
    drushFolder = expanduser('~') + '/.drush'
    drushFile = drushFolder + "/" + aliasFileName
    if os.path.isfile(drushFile):
      ret = True
    else:
      if not os.path.isdir(drushFolder):
        try:
          os.makedirs(drushFolder)
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
    updates = []
    for x in lst:
      # build list of updates in a list,
      # when you hit a blank line you are done
      # note: if there are no updates the first line will be blank
      if x:
        updates.append(x)
      else:
        break
    return updates

  def call(self, commands, alias = '', jsonRet = False):
    # FIXME: Allow commands ro be run on all drupdates sites at one time
    # ie drush @drupdates <some command>
    """ Run a drush comand and return a list/dictionary of the results

    Keyword arguments:
    commands -- list containing command, arguments and options
    alias -- drush site alias of site where "commands" to run on
    json -- binary deermining if the given command can/should return json

    """
    # https://github.com/dsnopek/python-drush/, threw errors calling Drush()
    # consider --strict=no
    if alias:
      commands.insert(0, '@drupdates.' + alias)
    if jsonRet:
      commands.append('--format=json')
    commands.insert(0, 'drush')
    # run the command
    try:
      popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
      print "Cannot run drush.call(), most likely because python can't find drush\n Error: ".format(e.strerror)
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
    """ Import a SQL dump using drush sqlc

    alias -- A Drush alias

    """
    workingDir = self.localsettings.get('workingDir')
    backportDir = self.localsettings.get('backupDir')
    commands = ['drush', '@' + alias, 'sqlc']
    popen = subprocess.Popen(commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    out, stderr = popen.communicate(file(backportDir + alias + '.sql').read())
    if stderr:
      print alias + " DB import error: " + stderr
      return False

    return True


