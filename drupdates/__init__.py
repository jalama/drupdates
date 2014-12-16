#!/usr/bin/env python

import requests
import subprocess
import git
import json
import os
import shutil
import datetime

try:
  from html import escape  # py3
except ImportError:
  from cgi import escape

from git import *

'''
Requirements:
Python v2.6+
Python Modules:
requests, GitPython, PyYAML
To install pip on CentOS:
sudo yum install python-pip
'''

"""
plan laid out at
@see https://www.evernote.com/l/AAIYsOFoMVlOVZsz6f-5SEL4s4SIRS2GfOY
"""

"""
I had issues getting the request module to load after I loaded it with pip
@see http://stackoverflow.com/questions/25276329/cant-load-python-modules-installed-via-pip-from-site-packages-directory
"""

'''
Note: you need an ssh key set up with Stash to make this script work
'''

# This should get replaced by a generic plugin for PM VCS systems
def apiCall (uri, name, method = 'get', **kwargs):
  #user = '', pword = ''):
  """ Perform and API call, expecting a JSON response.  Largely a wrapper
  around the request module

  Keyword arguments:
  uri -- the uri of the Restful Web Service (required)
  name -- the human readable label for the service being called (required)
  method -- HTTP method to use (defaul = 'get')
  kwargs -- dictionary of arguments passed directly to requests module method

  """
  # FIXME: need to HTML escape passwords
  func = getattr(requests, method)
  args = {}
  for key, value in kwargs.iteritems():
    args[key] = value
  # if not user == '' and not pword == '':
  #   args.append("auth=(user, pword)")
  print (args)
  r = func(uri, **args)
  responseDictionary = r.json()
  #If API call errors out print the error and quit the script
  if r.status_code != 200:
    if 'errors' in responseDictionary:
      errors = responseDictionary.pop('errors')
      firstError = errors.pop()
    elif 'error' in responseDictionary:
      firstError = responseDictionary.pop('error')
    else:
      firstError['message'] = "No error message provided by response"
    print("{0} returned an error, exiting the script.\n   Status Code: {1} \n Error: {2}".format(name, r.status_code , firstError['message']))
    return False
  else:
    return responseDictionary

def readUpdateReport(lst, updates = []):
  for x in lst:
    # build list of updates in a list,
    # when you hit a blank line you are done
    # note: if there are no updates the first line will be blank
    if not x == '':
      updates += x
    else:
      break

  return updates

def callDrush(commands, alias = '', jsonRet = False):
  """ Run a drush comand and return a list/dictionary of the results

  Keyword arguments:
  commands -- list containing command, arguments and options
  alias -- drush site alias of site where "commands" to run on
  json -- binary deermining if the given command can/should return json

  """
  # https://github.com/dsnopek/python-drush/, threw errors calling Drush()
  # consider --strict=no
  if not alias == '':
    commands.insert(0, '@' + alias)
  if jsonRet:
    commands.append('--format=json')
  commands.insert(0, 'drush')
  # run the command
  print commands
  popen = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = popen.communicate()
  if jsonRet:
    ret = json.loads(stdout)
  else:
    ret = stdout.split('\n')

  return ret

def importDrush(alias):
  """ Import a SQL dump using drush sqlc

  alias -- A Drush alias

  """
  commands = ['drush', '@' + alias, 'sqlc']
  popen = subprocess.Popen(cmds, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
  out, stderr = popen.communicate(file(backportDir + siteName + '.sql').read())
  if not stderr == '':
    print alias + " DB import error: " + stderr
    return False

  return True

def nextFriday():
  # Get the data string for the following Friday
  today = datetime.date.today()
  if datetime.datetime.today().weekday() == 4:
    friday = str(today + datetime.timedelta( (3-today.weekday())%7+1 ))
  else:
    friday = str(today + datetime.timedelta( (4-today.weekday()) % 7 ))
  return friday

def getAtTaskSession():
  # Get a session ID from AtTask
  atParams = {'username': pmUser, 'password': pmPword}
  response = apiCall(pmURL, pmLabel, 'post', params = atParams)
  if response == False:
    return response
  else:
    sessionID = responseDictionary['data']['sessionID']
    return sessionID


def submitAtTaskDeploy(env, description, targetDate, sessionID):
  """ Submit a Deployment request to AtTask

  env -- the Name of the environment to deploy to
  description -- the description test to go in the task
  targetDate -- the date to put in the lable fo the ticket
  sessionID -- The session ID form AtTask that authenticates this submission

  """
  sessparam = {'SessionID': sessionID}
  title = env + ' Deployment for ' + siteName +' w.e. ' + targetDate
  atParams = {'name': title, 'projectID': webMaintProjectID, 'teamID': webOpsTeamID, 'description': description}
  response = apiCall(pmURL, pmLabel, 'post', params = atParams, headers = sessparam)
  # r = requests.post('baseAtTaskUrl+taskAtTaskURL', params = params2, headers = sessparam)
  return response

def gitRepos():
  #Get list of Stash repos in the Rain Project.
  r = apiCall(gitRepoURL, gitRepoName, 'get', auth=(user, pword))
  repos = r['values']
  return repos

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
