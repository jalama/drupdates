""" Module handles the heavy lifting, building the various seit directories. """
import distutils.core, tempfile, git, shutil, os, yaml
from drupdates.utils import utils
from drupdates.settings import Settings
from drupdates.drush import Drush
from git import *

class siteupdate():

  def __init__(self, siteName, ssh):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)
    self.workingBranch = self.settings.get('workingBranch')
    self._siteName = siteName
    self.siteDir = os.path.join(self.settings.get('workingDir'), self._siteName)
    self.upCmds = self.settings.get('upCmds')
    self.upsCmds = self.settings.get('upsCmds')
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
  def upsCmds(self):
      return self._upsCmds
  @upsCmds.setter
  def upsCmds(self, value):
      self._upsCmds = value

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

  @property
  def repoStatus(self):
      return self._repoStatus
  @repoStatus.setter
  def repoStatus(self, value):
      self._repoStatus = value

  @property
  def _moduleDir(self):
      return self.__moduleDir
  @_moduleDir.setter
  def _moduleDir(self, value):
      self.__moduleDir = value

  def update(self):
    """ Set-up to and run Drush update(s) (i.e. up or ups). """
    utils.check_working_dir(self.settings.get('workingDir'))
    report = {}
    self.utilities.sysCommands(self, 'preUpdateCmds')
    stCmds = ['st']
    self.repoStatus = Drush.call(stCmds, self._siteName, True)
    if not isinstance(self.repoStatus, dict):
      report['status'] = "Repo {0} failed call to drush status during update".format(self._siteName)
      return report
    # Ensure update module is enabled.
    Drush.call(['en', 'update', '-y'], self._siteName)
    updates = self.runUpdates()
    # If no updates move to the next repo
    if not updates:
      self.commitHash = ""
      report['status'] = "Did not have any updates to apply"
      return report
    msg = '\n'.join(updates)
    # Call dr.call() without site alias argument, aliaes comes after dd argument
    dd = Drush.call(['dd', '@drupdates.' + self._siteName])
    self.siteWebroot = dd[0]
    if self.settings.get('buildSource') == 'make':
      shutil.rmtree(self.siteWebroot)
    else:
      rebuilt = self.rebuildWebRoot()
      if not rebuilt:
        report['status'] = "The webroot re-build failed."
        if self.settings.get('useMakeFile'):
          makeErr = " Ensure the make file format is correct "
          makeErr += "and Drush make didn't fail on a bad patch."
          report['status'] += makeErr
        return report
    gitRepo = self.gitChanges()
    commitAuthor = self.settings.get('commitAuthor')
    gitRepo.commit(m=msg, author=commitAuthor)
    self.commitHash = gitRepo.rev_parse('head')
    push = gitRepo.push(self._siteName, self.workingBranch)
    report['status'] = "The following updates were applied \n {0}".format(msg)
    report['commit'] = "The commit hash is {0}".format(self.commitHash)
    self.utilities.sysCommands(self, 'postUpdateCmds')
    return report

  def runUpdates(self):
    """ Run the site updates.

    The updates are done either by downloading the updates, updating the make
    file or both.

    """
    updates = False
    if self.settings.get('useMakeFile'):
      updatesRet = Drush.call(self.upsCmds, self._siteName, True)
      if isinstance(updatesRet, dict):
        updates = []
        for module, update in updatesRet.iteritems():
          api = update['api_version']
          current = update['existing_version'].replace(api + '-', '')
          candidate = update['candidate_version'].replace(api + '-', '')
          self.updateMakeFile(module, current, candidate)
          updates.append("Update {0} from {1} to {2}".format(module, current, candidate))
      if not self.settings.get('buildSource') == 'make':
        self.utilities.makeSite(self._siteName, self.siteDir)
    else:
      updatesRet = Drush.call(self.upCmds, self._siteName)
      updates = self.readUpdateReport(updatesRet)
    return updates

  def readUpdateReport(self, lst, updates = []):
    """ Read the report produced the the Drush pm-update command. """
    updates = []
    for x in lst:
      # build list of updates, when you hit a blank line you are done
      # note: if there are no updates the first line will be blank
      if x:
        updates.append(x)
      else:
        break
    if len(updates) <= 1:
      updates = False
    return updates

  def updateMakeFile(self, module, current, candidate):
    """ Update the make file.

    Keyword arguments:
    module -- the drupal module or core (required)
    current -- the current version
    candidate -- the version to update two

    """
    makeFile = self.utilities.findMakeFile(self._siteName, self.siteDir)
    makeFormat = self.settings.get('makeFormat')
    if makeFormat == 'make':
      f = open(makeFile)
      makef = f.read()
      f.close()
      currentStr = 'projects[{0}][version] = \"{1}\"'.format(module, current)
      candidateStr = 'projects[{0}][version] = \"{1}\"'.format(module, candidate)
      newdata = makef.replace(currentStr, candidateStr)
      f = open(makeFile, 'w')
      f.write(newdata)
      f.close()
    elif makeFormat == 'yaml':
      make = open(makeFile)
      makef = yaml.load(make)
      make.close()
      makef['projects'][module]['version'] = candidate
      f = open(makeFile, 'w')
      yaml.dump(makef, f, default_flow_style=False)

  def gitChanges(self):
    """ add/remove changed files, ignore file mode changes. """
    os.chdir (self.siteDir)
    repository = Repo(self.siteDir)
    gitRepo = repository.git
    if self._moduleDir and self.settings.get('ignoreCustomModules'):
      customModuleDir = os.path.join(self.siteWebroot, self._moduleDir, 'custom')
      try:
        gitRepo.checkout(customModuleDir)
      except git.exc.GitCommandError as e:
        print "Failed to re-instantiate the custom modules folder \n {0}".format(e)
    g = git.Git('.')
    g.config("core.fileMode", "false")
    gitRepo.add('./')
    deleted = gitRepo.ls_files('--deleted')
    for f in deleted.split():
      gitRepo.rm(f)
    return gitRepo

  def rebuildWebRoot(self):
    """ Rebuild the web root folder completely after running pm-update.

    Drush pm-update of Drupal Core deletes the .git folder therefore need to
    move the updated folder to a temp dir and re-build the webroot folder.

    """
    tempDir = tempfile.mkdtemp(self._siteName)
    shutil.move(self.siteWebroot, tempDir)
    addDir = self.settings.get('webrootDir')
    if addDir:
      repository = Repo(self.siteDir)
      gitRepo = repository.git
      gitRepo.checkout(addDir)
    else:
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
      addDir = self._siteName
    self._moduleDir = self.repoStatus.get('modules', "")
    if self._moduleDir:
      shutil.rmtree(os.path.join(self.siteWebroot, self._moduleDir))
    themeDir = self.repoStatus.get('themes', "")
    if themeDir:
      shutil.rmtree(os.path.join(self.siteWebroot, themeDir))
    self.utilities.rmCommon(self.siteWebroot, tempDir)
    try:
      distutils.dir_util.copy_tree(tempDir + '/' + addDir, self.siteWebroot)
    except IOError as e:
      print "Could not copy updates from {0} temp diretory to {1} \n Error: {2}".format(tempDir, self.siteWebroot, e.strerror)
      return False
    shutil.rmtree(tempDir)
    return True
