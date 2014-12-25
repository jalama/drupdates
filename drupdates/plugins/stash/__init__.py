from drupdates.utils import *

'''
Note: you need an ssh key set up with Stash to make this script work
'''
class stash(Plugin):

  # def __init__(self):
    # super(stash, self).__init__()

  def gitRepos(self):
    #Get list of Stash repos in the Rain Project.
    stashURL = settings.get('stashURL')
    gitRepoName = settings.get('gitRepoName')
    stashUser = settings.get('stashUser')
    stashPword = settings.get('stashPword')
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
