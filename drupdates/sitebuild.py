from drupdates.utils import *
from drupdates.drush import *
from drupdates.datastores import *
import git, shutil
from git import *

class sitebuild():

  def __init__(self, siteName, ssh):
    self.settings = Settings()
    self.workingDir = self.settings.get('workingDir')
    self.workingBranch = self.settings.get('workingBranch')
    self.siteName = siteName
    self.siteDir = self.workingDir + siteName
    self.ssh = ssh

  @property
  def workingDir(self):
      return self._workingDir
  @workingDir.setter
  def workingDir(self, value):
      self._workingDir = value

  @property
  def siteName(self):
      return self._siteName
  @siteName.setter
  def siteName(self, value):
      self._siteName = value

  @property
  def siteDir(self):
      return self._siteDir
  @siteDir.setter
  def siteDir(self, value):
    self._siteDir = value

  @property
  def workingBranch(self):
      return self._workingBranch
  @workingBranch.setter
  def workingBranch(self, value):
      self._workingBranch = value

  @property
  def ssh(self):
      return self._ssh
  @ssh.setter
  def ssh(self, value):
      self._ssh = value

  def build(self):
    # Build Git repository
    # http://nullege.com/codes/search/git.add
    dr = drush()
    if os.path.isdir(self.siteDir):
      try:
        shutil.rmtree(self.siteDir)
      except OSError as e:
        print "Cannot remove the site directory\n Error: {0}".format(e.strerror)
        return False
    repository = Repo.init(self.siteDir)
    remote = git.Remote.create(repository, self.siteName, self.ssh)
    try:
      remote.fetch(self.workingBranch)
    except git.exc.GitCommandError as e:
      print "Git could could not checkout the {0} branch. \n Error: {1}".format(self.workingBranch, e)
      return False
    gitRepo = repository.git
    gitRepo.checkout('FETCH_HEAD')
    stCmds = ['st']
    repoStatus = dr.call(stCmds, self.siteName, True)
    drupalSite = repoStatus.get('drupal-version', "")
    # If this is not a Drupal repo move to the next repo
    if not drupalSite:
      return False
    bootstrap = repoStatus.get('bootstrap', "")
    if not bootstrap:
      # Re-build database if it fails go to the next repo

      buildDB = datastores().build(self.siteName)
      if not buildDB:
        return False
      # Perform Drush site-install to get a base settings.php file
      siCmds = ['si', 'minimal', '-y']
      install = dr.call(siCmds, self.siteName)
      dd = dr.call(['dd', '@drupdates.' + self.siteName])
      siteWebroot = dd[0]
      siFiles = self.settings.get('drushSiFiles')
      for f in siFiles:
        os.chmod(siteWebroot + f, 0777)
    if self.settings.get('importBackup'):
      # Import the backup file
      importDB = dr.dbImport(self.siteName)
      if not importDB:
        return False
    return True
