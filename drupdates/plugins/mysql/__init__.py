from drupdates.utils import *
from drupdates.drush import *
from drupdates.datastores import *
import os
from os.path import expanduser

class mysql(datastore):

  def __init__(self):
    # FIXME: class get re-instantiated each time db is cvalled
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.localsettings = Settings(self.currentDir)

  def writeMyCnf (self):
    # We have to create this file to get drush to run sql-create correctly
    # without ~/.my.cnf file drush sql-create won't pass the --db-su option
    # Sucks because it means we have to have sql driver specific plugins :(
    myFile = self.localsettings.get('mysqlSettingsFile')
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
      userline = "user = {0} \n".format(self.localsettings.get('datastoreSuperUser'))
      password = self.localsettings.get('datastoreSuperPword')
      settings = self.localsettings.get('mysqlSettings')
      f.write("This file was written by the Drupdates script\n")
      for setting in settings:
        settingline = "[{0}]\n".format(setting)
        f.write(settingline)
        f.write(userline)
        if not password == "None":
          passline = "password = {0} \n".format(password)
          f.write(passline)
        f.write("\n")
      f.close()
      ret = True
    return ret

  def create(self, site):
    if self.writeMyCnf():
      dr = drush()
      createCmds = ['sql-create', '-y', '--db-su=' + self.localsettings.get('datastoreSuperUser') ]
      dr.call(createCmds, site)
    return True

  def driverSettings(self):
    return self.localsettings





