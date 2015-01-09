import distutils.core, tempfile, os, git, shutil, copy
from drupdates.utils import *
from drupdates.drush import *
from git import *

class siteupdate():

  def __init__(self, siteName, ssh):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)
    self.workingDir = self.settings.get('workingDir')
    self.workingBranch = self.settings.get('workingBranch')
    self.siteName = siteName
    self.siteDir = self.workingDir + siteName
    self.upCmds = self.settings.get('upCmds')
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

  def update(self):
    # Run Drush up to update the site
    dr = drush()
    # Make sure update module is enabled
    dr.call(['en', 'update', '-y'], self.siteName)
    # upCmdsCopy = copy.copy(upCmds)
    updatesRet = dr.call(self.upCmds, self.siteName)
    updates = dr.readUpdateReport(updatesRet)
    # If there are no updates move to the next repo
    if len(updates) <= 1:
      return False
    dd = dr.call(['dd', '@drupdates.' + self.siteName])
    siteWebroot = dd[0]
    tempDir = tempfile.mkdtemp(self.siteName)
    shutil.move(siteWebroot, tempDir)
    # Commit and push updates to remote repo
    # FIXME: Need to rebuild any make file to reflect the new module versions
    # maybe using generate-makefile or simply search/replace?
    msg = '\n'.join(updates)
    repository = Repo.init(self.siteDir)
    try:
      remote = git.Remote.create(repository, self.siteName, self.ssh)
    except git.exc.GitCommandError as e:
      if not e.status == 128:
        print "Could not establish a remote for the {0} repo".format(self.siteName)
    remote.fetch(self.workingBranch)
    gitRepo = repository.git
    try:
      gitRepo.checkout('FETCH_HEAD', b=self.workingBranch)
    except git.exc.GitCommandError as e:
      gitRepo.checkout(self.workingBranch)
    try:
      distutils.dir_util.copy_tree(tempDir + '/' + self.siteName, siteWebroot)
    except IOError as e:
      print "Could not copy updates Drupal directory from temp to {0} \n Error: {1}".format(siteWebroot, e.strerror)
      return False
    shutil.rmtree(tempDir)
    os.chdir (siteWebroot)
    g = git.Git('.')
    fileMode = g.config("core.fileMode")
    g.config("core.fileMode", "false")
    gitRepo.add('./')
    commitAuthor = self.settings.get('commitAuthor')
    gitRepo.commit(m=msg, author=commitAuthor)
    commitHash = gitRepo.rev_parse('head')
    push = gitRepo.push(self.siteName)
    g.config("core.fileMode", fileMode)
    report = {}
    report['status'] = "The following updates were applied \n {0}".format(msg)
    report['commit'] = "The commit hash is {0}".format(commitHash)
    return report


