#!/usr/bin/env python

from drupdates.utils import *
from drupdates.drush import *
from drupdates.repos import *
from drupdates.pmtools import *
import git
import os
import shutil

from git import *

'''
Requirements:
Python v2.6+
'''

"""
plan laid out at
@see https://www.evernote.com/l/AAIYsOFoMVlOVZsz6f-5SEL4s4SIRS2GfOY
"""

"""
I had issues getting the request module to load after I loaded it with pip
@see http://stackoverflow.com/questions/25276329/cant-load-python-modules-installed-via-pip-from-site-packages-directory
"""

def main():
  workingDir = settings.get('workingDir')
  backportDir = settings.get('backupDir')
  # FIXME: this is assuming the site alias and site directory are one in the same
  # our vagrant install populates the sa list based on the direcotry being populated
  report = {}
  repoTool = repos()
  repos = repoTool.get()
  blacklist = settings.get('blacklist')
  subprocess.call(['drush', 'cache-clear', 'drush'])
  for siteName, ssh in repos.iteritems():
    # Check to see if this site is in the user's blacklist
    if siteName in blacklist:
      continue
    siteDir = workingDir + '/' + siteName
    os.chdir(workingDir)
    if os.path.isdir(siteName):
      shutil.rmtree(siteName)
    # Build Git repository
    # http://nullege.com/codes/search/git.add
    # FIXME: this is backwards as you would usually choose the target directory based on the drush site alias target directory
    repository = Repo.clone_from(ssh, siteDir)
    git = repository.git
    git.checkout(b = settings.get('workingBranch'))
    stCmds = ['st']
    repoStatus = callDrush(stCmds, siteName, True)
    status = repoStatus.get('drupal-version', False)
    # If this is not a Drupal repo move to the next repo
    if status == False:
      continue
    os.chdir (siteDir)
    # Import a DB backup, if it fails go to the next repo
    importDB = importDrush(siteName)
    if not importDB:
      continue
    # Run Drush up to update the site
    # Make sure update module is enabled
    callDrush(['en', 'update', '-y'], siteName)
    upCmds = upCmds = settings.get('upCmds')
    upCmds.insert(0, 'up')
    drush = callDrush(upCmds, siteName)
    updates = readUpdateReport(drush)
    # If there are no updates move to the next repo
    if len(updates) == 0:
      report[siteName]['status']= "{0} did not have any updates to apply".format(siteName)
      continue
    # Commit and push updates to remote repo
    # FIXME: Need to rebuild the Make file to reflect the new module versions
    # maybe using generate-makefile or simply search/replace
    git.add('./')
    msg = '\n'.join(updates)
    git.commit(m=msg, author=commitAuthor)
    commitHash = git.rev_parse('head')
    push = git.push(remote="origin", branches=workingBranch, dry_run=False)
    report[siteName]['status'] = "{0} applied the following update {1}".format(siteName, msg)
    report[siteName]['commit'] = "The commit hash is {0}".format(commitHash)
    # AtTask Deployment ticket submission
    descriptionList = []
    descriptionList.append("Git Hash = <" + commitHash + "> \n")
    descriptionList.append("Post deplayment steps: \n")
    descriptionList.append("drush @" + siteName +" updb -y \n")
    description = '\n'.join(descriptionList)
    friday = nextFriday()
    pmTool = pmtools()
    # Staging Ticket
    staging = pmtool.deploy(siteName, 'Staging', description, friday, commitHash)
    if staging:
      report[siteName] = staging
    #Production Ticket
    production = pmtool.deploy(siteName, 'Production', description, friday, commitHash)
    if production:
      report[siteName] = production
  print (report)
