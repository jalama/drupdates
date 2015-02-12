from drupdates.utils import *
from drupdates.drush import *
from drupdates.constructors.datastores import *
import git, shutil
from git import *

class sitebuild():

  def __init__(self, siteName, ssh):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)
    self._workingBranch = self.settings.get('workingBranch')
    self._siteName = siteName
    self.siteDir = self.settings.get('workingDir') + self._siteName
    self.ssh = ssh
    self.dr = drush()
    self.utilities = utils()

  @property
  def _siteName(self):
      return self.__siteName
  @_siteName.setter
  def _siteName(self, value):
      self.__siteName = value

  @property
  def siteDir(self):
      return self._siteDir
  @siteDir.setter
  def siteDir(self, value):
    self._siteDir = value

  @property
  def _workingBranch(self):
      return self.__workingBranch
  @_workingBranch.setter
  def _workingBranch(self, value):
      self.__workingBranch = value

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
    """ Build site folder from Git repository."""
    if not utils.removeDir(self.siteDir):
      return False
    self.utilities.sysCommands(self, 'preBuildCmds')
    repository = Repo.init(self.siteDir)
    remote = git.Remote.create(repository, self._siteName, self.ssh)
    try:
      remote.fetch(self._workingBranch)
    except git.exc.GitCommandError as e:
      print "Git could could not checkout the {0} branch for {1}. \n Error: {2}".format(self._workingBranch, self._siteName, e)
      return False
    gitRepo = repository.git
    gitRepo.checkout('FETCH_HEAD', b=self._workingBranch)
    if self.settings.get('useMakeFile'):
      make = self.makeSite()
    stCmds = ['st']
    repoStatus = drush.call(stCmds, self._siteName, True)
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
    self.utilities.sysCommands(self, 'postBuildCmds')
    return ret

  def constructSite(self):
    """ Rebulid the Drupal site: build DB, settings.php, etc..."""
    buildDB = datastores().build(self._siteName)
    if not buildDB:
      return False
    # Perform Drush site-install to get a base settings.php file
    siCmds = ['si', 'minimal', '-y']
    install = drush.call(siCmds, self._siteName)
    stCmds = ['st']
    repoStatus = drush.call(stCmds, self._siteName, True)
    bootstrap = repoStatus.get('bootstrap', "")
    if not bootstrap:
      return False
    dd = drush.call(['dd', '@drupdates.' + self._siteName])
    self.siteWebroot = dd[0]
    siFiles = self.settings.get('drushSiFiles')
    for f in siFiles:
      os.chmod(self.siteWebroot + f, 0777)
    return True

  def importBackup(self):
    """ Imprt a site back-up

    Note: the back-up sife most follow the <siteName>.sql" naming convention"

    """
    importDB = self.dr.dbImport(self._siteName)
    return importDB

  def makeSite(self):
    """ Build a webroot based on a make file. """
    webRoot = self.settings.get('webrootDir')
    folder = self.siteDir +'/' + webRoot
    makeFile = self.utilities.findMakeFile(self._siteName, self.siteDir)
    utils.removeDir(folder)
    if makeFile and webRoot:
      # Run drush make
      # Get the repo webroot
      makeCmds = ['make', makeFile, folder]
      make = drush.call(makeCmds)
