import distutils.core, tempfile, os, git, shutil, copy
from drupdates.utils import *
from drupdates.drush import *
from git import *

class siteupdate():

  def __init__(self, siteName, ssh):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)
    self.workingBranch = self.settings.get('workingBranch')
    self._siteName = siteName
    self.siteDir = self.settings.get('workingDir') + self._siteName
    self.upCmds = self.settings.get('upCmds')
    self.ssh = ssh
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
  def workingBranch(self):
      return self._workingBranch
  @workingBranch.setter
  def workingBranch(self, value):
      self._workingBranch = value

  @property
  def upCmds(self):
      return self._upCmds
  @upCmds.setter
  def upCmds(self, value):
      self._upCmds = value

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

  @property
  def commitHash(self):
      return self._commitHash
  @commitHash.setter
  def commitHash(self, value):
      self._commitHash = value

  def update(self):
    """ Set-up to and run Drush pm-update (i.e. up) to update the site."""
    report = {}
    self.utilities.sysCommands(self, 'preUpdateCmds')
    dr = drush()
    # Make sure update module is enabled
    dr.call(['en', 'update', '-y'], self._siteName)
    # upCmdsCopy = copy.copy(upCmds)
    updatesRet = dr.call(self.upCmds, self._siteName)
    updates = dr.readUpdateReport(updatesRet)
    # If there are no updates move to the next repo
    if len(updates) <= 1:
      self.commitHash = ""
      report['status'] = "Did not have any updates to apply"
      return report
    dd = dr.call(['dd', '@drupdates.' + self._siteName])
    self.siteWebroot = dd[0]
    tempDir = tempfile.mkdtemp(self._siteName)
    shutil.move(self.siteWebroot, tempDir)
    # Commit and push updates to remote repo
    # FIXME: Need to rebuild any make file to reflect the new module versions
    # maybe using generate-makefile or simply search/replace?
    msg = '\n'.join(updates)
    repository = Repo.init(self.siteDir)
    try:
      remote = git.Remote.create(repository, self._siteName, self.ssh)
    except git.exc.GitCommandError as e:
      if not e.status == 128:
        print "Could not establish a remote for the {0} repo".format(self._siteName)
    remote.fetch(self.workingBranch)
    gitRepo = repository.git
    try:
      gitRepo.checkout('FETCH_HEAD', b=self.workingBranch)
    except git.exc.GitCommandError as e:
      gitRepo.checkout(self.workingBranch)
    try:
      distutils.dir_util.copy_tree(tempDir + '/' + self._siteName, self.siteWebroot)
    except IOError as e:
      print "Could not copy updates Drupal directory from temp to {0} \n Error: {1}".format(self.siteWebroot, e.strerror)
      return False
    shutil.rmtree(tempDir)
    os.chdir (self.siteWebroot)
    g = git.Git('.')
    fileMode = g.config("core.fileMode")
    g.config("core.fileMode", "false")
    gitRepo.add('./')
    commitAuthor = self.settings.get('commitAuthor')
    gitRepo.commit(m=msg, author=commitAuthor)
    self.commitHash = gitRepo.rev_parse('head')
    push = gitRepo.push(self._siteName, self.workingBranch)
    g.config("core.fileMode", fileMode)
    report['status'] = "The following updates were applied \n {0}".format(msg)
    report['commit'] = "The commit hash is {0}".format(self.commitHash)
    self.utilities.sysCommands(self, 'postUpdateCmds')
    return report


