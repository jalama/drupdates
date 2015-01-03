from drupdates.utils import *
from drupdates.drush import *
from drupdates.repos import *
from drupdates.pmtools import *
from drupdates.datastores import *
import distutils.core
import tempfile
import os
import shutil
import git
import copy
from git import *

def main():
  settings = Settings()
  workingDir = settings.get('workingDir')
  backportDir = settings.get('backupDir')
  upCmds = settings.get('upCmds')
  upCmds.insert(0, 'up')
  # FIXME: this is assuming the site alias and site directory are one in the same
  # our vagrant install populates the sa list based on the direcotry being populated
  report = {}
  dr = drush()
  repoTool = repos()
  sites = repoTool.get()
  db = datastores()
  pmTool = pmtools()
  blacklist = settings.get('blacklist')
  for siteName, ssh in sites.iteritems():
    # Check to see if this site is in the user's blacklist
    if siteName in blacklist:
      continue

    # Build Git repository
    # http://nullege.com/codes/search/git.add
    siteDir = workingDir + siteName
    os.chdir(workingDir)
    if os.path.isdir(siteName):
      try:
        shutil.rmtree(siteName)
      except OSError as e:
        print "Cannot remove the site directory\n Error: {0}".format(e.strerror)
        continue
    repository = Repo.init(siteDir)
    remote = git.Remote.create(repository, siteName, ssh)
    workingBranch = settings.get('workingBranch')
    try:
      remote.fetch(workingBranch)
    except git.exc.GitCommandError as e:
      print "Git could could not checkout the {0} branch. \n Error: {1}".format(workingBranch, e)
      continue
    gitRepo = repository.git
    gitRepo.checkout('FETCH_HEAD')
    stCmds = ['st']
    repoStatus = dr.call(stCmds, siteName, True)
    status = repoStatus.get('drupal-version', False)
    # If this is not a Drupal repo move to the next repo
    if status == False:
      continue
    os.chdir (siteDir)
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
    # Import the backup file
    importDB = dr.dbImport(siteName)
    if not importDB:
      continue

    # Run Drush up to update the site
    # Make sure update module is enabled
    report[siteName] = {}
    dd = dr.call(['dd', '@drupdates.' + siteName])
    siteWebroot = dd[0]
    os.chdir (siteWebroot)
    os.chdir ('..')
    dr.call(['en', 'update', '-y'], siteName)
    upCmdsCopy = copy.copy(upCmds)
    updatesRet = dr.call(upCmdsCopy, siteName)
    updates = dr.readUpdateReport(updatesRet)
    # If there are no updates move to the next repo
    if len(updates) == 0:
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
      gitRepo.checkout('dev')
    distutils.dir_util.copy_tree(tempDir + '/' + siteName, siteDir)
    shutil.rmtree(tempDir)
    # FIXME: gitRep.set_config_option('core.fileMode', 'false')
    gitRepo.add('./')
    commitAuthor = settings.get('commitAuthor')
    gitRepo.commit(m=msg, author=commitAuthor)
    commitHash = gitRepo.rev_parse('head')
    push = gitRepo.push(siteName)
    report[siteName]['status'] = "The following updates were applied \n {0}".format(msg)
    report[siteName]['commit'] = "The commit hash is {0}".format(commitHash)

    # Deployment ticket submission
    tickets = settings.get('deploymentTickets')
    deploys = pmTool.deployTicket(siteName, tickets, commitHash)
    report[siteName]['pmtool'] = deploys
  print (report)
