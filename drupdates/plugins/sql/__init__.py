from drupdates.utils import *
from drupdates.drush import *
from drupdates.constructors.datastores import *
import os
from os.path import expanduser

class sql(datastore):

  def __init__(self):
    # FIXME: class get re-instantiated each time db is called
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

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
      os.remove(localFile)
      return True
    else:
      return False

  def create(self, site):
    """ Create a MYSQL Database."""
    driver = self.settings.get('datastoreDriver')
    spwd = self.settings.get('datastoreSuperPword')
    suser = self.settings.get('datastoreSuperUser')
    if driver == 'mysql' and not spwd:
      if not self.writeMyCnf():
        return False
    dr = drush()
    createCmds = ['sql-create', '-y', '--db-su=' + suser, '--db-su-pw=' + spwd]
    dr.call(createCmds, site)
    self.deleteFiles()
    return True

  def driverSettings(self):
    """ Return the MYSQL Driver settings.

    Note: this is used to pass settings to the Drush Alias file.

    """
    return self.settings





