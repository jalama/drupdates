#!/usr/bin/env python

from . import utils
from . import drush
from pmtools import *
from repotools import *
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
  repos = gitRepos()
  report = []
  subprocess.call(['drush', 'cache-clear', 'drush'])
  for repo in repos:
    siteName = repo['slug']
    siteDir = WORKING_DIR + '/' + siteName
    os.chdir(WORKING_DIR)
    if os.path.isdir(siteName):
      shutil.rmtree(siteName)
    for link in repo['links']['clone']:
      if link['name'] == 'ssh':
        ssh = link['href']
        # Build Git repository
        # http://nullege.com/codes/search/git.add
        repository = Repo.clone_from(ssh, siteDir)
        git = repository.git
        git.checkout(b =workingBranch)
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
        upCmds = ['up', '-y', '--security-only', '--no-backup']
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
        sessionID = getAtTaskSession()
        # Staging Ticket
        staging = submitAtTaskDeploy('Staging', description, friday, sessionID)
        if staging:
          data = staging['data']
          report[siteName]['staging'] = "The Staging deploy ticket is {0}task/view/?ID={1}".format(baseAtTaskUrl, data['ID'])
        #Production Ticket
        production = submitAtTaskDeploy('Production', description, friday, sessionID)
        if production:
          data = prod['data']
          report[siteName]['production'] = "The Production deploy ticket is {0}task/view/?ID={1}".format(baseAtTaskUrl, data['ID'])
  print (report)

"""
Example: https://highlights.cr1.attasksandbox.com/task/view?ID=548cb1470000090f9d24bf983a32fa9e
>>> print response
{u'data': {u'status': u'NEW', u'workRequired': 0, u'name': u'test task by jim', u'plannedStartDate': u'2013-11-21T09:00:00:000-0500', u'progressStatus': u'LT', u'taskNumber': 702, u'objCode': u'TASK', u'projectedStartDate': u'2014-12-15T09:00:00:000-0500', u'wbs': u'588', u'priority': 0, u'percentComplete': 0.0, u'projectedCompletionDate': u'2014-12-15T09:00:00:000-0500', u'ID': u'548cb1470000090f9d24bf983a32fa9e', u'plannedCompletionDate': u'2013-11-21T09:00:00:000-0500'}}

"""
