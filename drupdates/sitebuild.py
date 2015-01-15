from drupdates.updates import *
from drupdates.drush import *
from drupdates.datastores import *
import git, shutil
from git import *

class sitebuild():

  def __init__(self, siteName, ssh):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)
    self.workingDir = self.settings.get('workingDir')
    self.workingBranch = self.settings.get('workingBranch')
    self.siteName = siteName
    self.siteDir = self.workingDir + siteName
    self.ssh = ssh
    self.dr = drush()

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

  @property
  def siteWebRoot(self):
      return self._siteWebRoot
  @siteWebRoot.setter
  def siteWebRoot(self, value):
      self._siteWebRoot = value

  def build(self):
    # Build Git repository
    # http://nullege.com/codes/search/git.add
    if os.path.isdir(self.siteDir):
      try:
        shutil.rmtree(self.siteDir)
      except OSError as e:
        print "Cannot remove the site directory\n Error: {0}".format(e.strerror)
        return False
    sysCommands(self, 'preBuildCmds')
    repository = Repo.init(self.siteDir)
    remote = git.Remote.create(repository, self.siteName, self.ssh)
    try:
      remote.fetch(self.workingBranch)
    except git.exc.GitCommandError as e:
      print "Git could could not checkout the {0} branch. \n Error: {1}".format(self.workingBranch, e)
      return False
    gitRepo = repository.git
    gitRepo.checkout('FETCH_HEAD', b=self.workingBranch)
    stCmds = ['st']
    repoStatus = self.dr.call(stCmds, self.siteName, True)
    drupalSite = repoStatus.get('drupal-version', "")
    # If this is not a Drupal repo move to the next repo
    if not drupalSite:
      return False
    bootstrap = repoStatus.get('bootstrap', "")
    ret = True
    if not bootstrap:
      # Re-build database if it fails go to the next repo
      ret = self.constructSite()
    if ret and self.settings.get('importBackup'):
      # Import the backup file
      ret = self.importBackup()
    sysCommands(self, 'postBuildCmds')
    return ret

  def constructSite(self):
    buildDB = datastores().build(self.siteName)
    if not buildDB:
      return False
    # Perform Drush site-install to get a base settings.php file
    siCmds = ['si', 'minimal', '-y']
    install = self.dr.call(siCmds, self.siteName)
    dd = self.dr.call(['dd', '@drupdates.' + self.siteName])
    self.siteWebroot = dd[0]
    siFiles = self.settings.get('drushSiFiles')
    for f in siFiles:
      os.chmod(self.siteWebroot + f, 0777)
    return True

  def importBackup(self):
    importDB = self.dr.dbImport(self.siteName)
    return importDB
