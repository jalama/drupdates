from drupdates.utils import *
from drupdates.repos import *

'''
Note: you need an ssh key set up with Stash to make this script work
'''

class stash(repoTool):

  def __init__(self):
    currentDir = os.path.dirname(os.path.realpath(__file__))
    self.localsettings = Settings(currentDir)

  def gitRepos(self):
    #Get list of Stash repos in the Rain Project.
    stashURL = self.localsettings.get('stashURL')
    gitRepoName = self.localsettings.get('gitRepoName')
    stashUser = self.localsettings.get('stashUser')
    stashPword = self.localsettings.get('stashPword')
    r = apiCall(stashURL, gitRepoName, 'get', auth=(stashUser, stashPword))
    if not r == False:
      repos = self.__parseRepos(r['values'])
      return repos
    else:
      return {}

  def __parseRepos(self, raw):
  	repos = {}
  	for repo in raw:
  		for link in repo['links']['clone']:
  			if link['name'] == 'ssh':
  				repos[repo['slug']] = link['href']
  	return repos
