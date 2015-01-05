import distutils.core, tempfile, os, shutil, git, copy
from drupdates.utils import *
from drupdates.drush import *
from drupdates.repos import *
from drupdates.pmtools import *
from drupdates.datastores import *
from git import *

def main():
  settings = Settings()
  report = {}
  dr = drush()
  sites = repos().get()
  db = datastores()
  pmTool = pmtools()
  blacklist = settings.get('blacklist')
  singleSite = settings.get('singleSite')
  workingBranch = settings.get('workingBranch')
  workingDir = settings.get('workingDir')
  backportDir = settings.get('backupDir')
  upCmds = settings.get('upCmds')
  upCmds.insert(0, 'up')
  if singleSite:
    sites = {singleSite : sites[singleSite]}
  for siteName, ssh in sites.iteritems():
    report[siteName] = {}
    # Check to see if this site is in the user's blacklist
    if siteName in blacklist:
      continue

    if settings.get('buildRepos'):
      # Build Git repository
      # http://nullege.com/codes/search/git.add
      siteDir = workingDir + siteName
      if os.path.isdir(siteDir):
        try:
          shutil.rmtree(siteDir)
        except OSError as e:
          print "Cannot remove the site directory\n Error: {0}".format(e.strerror)
          continue
      repository = Repo.init(siteDir)
      remote = git.Remote.create(repository, siteName, ssh)
      try:
        remote.fetch(workingBranch)
      except git.exc.GitCommandError as e:
        print "Git could could not checkout the {0} branch. \n Error: {1}".format(workingBranch, e)
        continue
      gitRepo = repository.git
      gitRepo.checkout('FETCH_HEAD')
      stCmds = ['st']
      repoStatus = dr.call(stCmds, siteName, True)
      drupalSite = repoStatus.get('drupal-version', "")
      # If this is not a Drupal repo move to the next repo
      if not drupalSite:
        continue
      bootstrap = repoStatus.get('bootstrap', "")
      if not bootstrap:
        # Re-build database if it fails go to the next repo
        buildDB = db.build(siteName)
        if not buildDB:
          continue
        # Perform Drush site-install to get a base settings.php file
        siCmds = ['si', 'minimal', '-y']
        install = dr.call(siCmds, siteName)
        dd = dr.call(['dd', '@drupdates.' + siteName])
        siteWebroot = dd[0]
        siFiles = settings.get('drushSiFiles')
        for f in siFiles:
          os.chmod(siteWebroot + f, 0777)
      if settings.get('importBackup'):
        # Import the backup file
        importDB = dr.dbImport(siteName)
        if not importDB:
          continue

    if settings.get('runUpdates'):
      # Run Drush up to update the site
      # Make sure update module is enabled
      dd = dr.call(['dd', '@drupdates.' + siteName])
      siteWebroot = dd[0]
      os.chdir (siteWebroot)
      os.chdir ('..')
      dr.call(['en', 'update', '-y'], siteName)
      upCmdsCopy = copy.copy(upCmds)
      updatesRet = dr.call(upCmdsCopy, siteName)
      updates = dr.readUpdateReport(updatesRet)
      # If there are no updates move to the next repo
      if len(updates) == 1:
        report[siteName]['status']= "Did not have any updates to apply"
        continue
      else:
        tempDir = tempfile.mkdtemp(siteName)
        shutil.move(siteWebroot, tempDir)
      # Commit and push updates to remote repo
      # FIXME: Need to rebuild the Make file to reflect the new module versions
      # maybe using generate-makefile or simply search/replace?
      msg = '\n'.join(updates)
      repository = Repo.init(siteDir)
      try:
        remote = git.Remote.create(repository, siteName, ssh)
      except git.exc.GitCommandError as e:
        if not e.status == 128:
          print "Could not establish a remote for the {0} repo".format(siteName)
      remote.fetch('dev')
      gitRepo = repository.git
      try:
        gitRepo.checkout('FETCH_HEAD', b='dev')
      except git.exc.GitCommandError as e:
        gitRepo.checkout(workingBranch)
      try:
        distutils.dir_util.copy_tree(tempDir + '/' + siteName, siteWebroot)
      except IOError as e:
        print "Could not copy updates Drupal directory fomr temp to {0} \n Error: {1}".format(siteWebroot, e.strerror)
        continue
      shutil.rmtree(tempDir)
      os.chdir (siteWebroot)
      g = git.Git('.')
      fileMode = g.config("core.fileMode")
      g.config("core.fileMode", "false")
      gitRepo.add('./')
      commitAuthor = settings.get('commitAuthor')
      gitRepo.commit(m=msg, author=commitAuthor)
      commitHash = gitRepo.rev_parse('head')
      push = gitRepo.push(siteName)
      g.config("core.fileMode", fileMode)
      report[siteName]['status'] = "The following updates were applied \n {0}".format(msg)
      report[siteName]['commit'] = "The commit hash is {0}".format(commitHash)

    # Deployment ticket submission
    if settings.get('submitDeployTicket'):
      deploys = pmTool.deployTicket(siteName, commitHash)
      report[siteName]['pmtool'] = deploys
  dr.deleteFiles()
  print (report)
