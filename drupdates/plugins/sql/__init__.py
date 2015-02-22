from drupdates.utils import *
from drupdates.drush import *
from drupdates.constructors.datastores import *
import os
from os.path import expanduser
from string import Template

class sql(datastore):

  def __init__(self):
    # FIXME: class get re-instantiated each time db is called
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  @property
  def aliasFile(self):
    return self._aliasFile
  @aliasFile.setter
  def aliasFile(self, value):
    self._aliasFile = value

  def writeMyCnf (self):
    """ Create a my.cnf file.

    If the mysql root password = "" we have to create this file for drush to
    run sql-create correctly.
    Without ~/.my.cnf file drush sql-create won't pass the --db-su option.

    """
    myFile = self.settings.get('mysqlSettingsFile')
    localFile = expanduser('~') + '/' + myFile
    ret = False
    if os.path.isfile(localFile):
      ret = True
    else:
      try:
        f = open(localFile, 'w')
      except IOError as e:
        print "Could not wrtie the {0} file \n Error: {1}".format(localFile, e.strerror)
        return ret
      userline = "user = {0} \n".format(self.settings.get('datastoreSuperUser'))
      password = self.settings.get('datastoreSuperPword')
      settings = self.settings.get('mysqlSettings')
      f.write("#This file was written by the Drupdates script\n")
      for setting in settings:
        settingline = "[{0}]\n".format(setting)
        f.write(settingline)
        f.write(userline)
        if password:
          passline = "password = {0} \n".format(password)
          f.write(passline)
        f.write("\n")
      f.close()
      ret = True
    return ret

  def deleteFiles (self):
    """ Clean-up my.cnf file."""
    myFile = self.settings.get('mysqlSettingsFile')
    localFile = expanduser('~') + '/' + myFile
    if os.path.isfile(localFile):
      try:
        os.remove(localFile)
      except OSError as e:
        print "Clean-up error, could not remove {0} \n Error: {1}".format(localFile, e.strerror)
    if os.path.isfile(self.aliasFile):
      try:
        os.remove(self.aliasFile)
      except OSError as e:
        print "Clean-up error, could not remove {0} \n Error: {1}".format(self.AliasFile, e.strerror)
    return True

  def create(self, site):
    """ Create a MYSQL Database."""
    driver = self.settings.get('datastoreDriver')
    spwd = self.settings.get('datastoreSuperPword')
    suser = self.settings.get('datastoreSuperUser')
    if driver == 'mysql' and not spwd:
      if not self.writeMyCnf():
        return False
    createCmds = ['sql-create', '-y', '--db-su=' + suser, '--db-su-pw=' + spwd]
    drush.call(createCmds, site)
    return True

  def aliases(self):
    """ Build a Drush alias file in $HOME/.drush, with alises to be used later.

    Notes:
    The file name is controlled by the drushAliasFile settings
    All of the aliases will be prefixed with "drupdates" if he default file name
      is retained
    """

    ret = False
    aliasFileName = self.settings.get('drushAliasFile')
    drushFolder = expanduser('~') + '/.drush'
    drushFile = drushFolder + "/" + aliasFileName
    if not os.path.isdir(drushFolder):
      try:
        os.makedirs(drushFolder)
      except OSError as e:
        print "Could not create ~/.drush folder \n Error: {0}".format(e.strerror)
        return ret
    currentDir = os.path.dirname(os.path.realpath(__file__))
    # Symlink the Drush aliases file
    src = currentDir + "/templates/aliases.template"
    doc = open(src)
    s = Template(doc.read())
    doc.close()
    try:
      f = open(drushFile,'w')
    except OSError as e:
      print "Could not create {0} folder \n Error: {1}".format(drushFile, e.strerror)
      return ret
    webrootSet = self.settings.get('webrootDir')
    hostSet = self.settings.get('datastoreHost')
    driverSet = self.settings.get('datastoreDriver')
    pathSet = self.settings.get('workingDir')
    portSet = self.settings.get('datastorePort')
    f.write(s.safe_substitute(host=hostSet, driver=driverSet, path=pathSet, webroot=webrootSet, port=portSet))
    self.aliasFile = drushFile
    f.close()
    ret = True
    return ret







