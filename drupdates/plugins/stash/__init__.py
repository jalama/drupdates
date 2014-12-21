from drupdates.utils import *

'''
Note: you need an ssh key set up with Stash to make this script work
'''
class stash:

  def gitRepos(self):
    #Get list of Stash repos in the Rain Project.
    gitRepoURL = settings.get('gitRepoURL')
    gitRepoName = settings.get('gitRepoName')
    uname = settings.get('uname')
    pword = settings.get('pword')
    r = apiCall(gitRepoURL, gitRepoName, 'get', auth=(uname, pword))
    reposRaw = r['values']
    repos = self.__parseRepos(reposRaw)
    return repos

  def __parseRepos(self, raw):
  	repos = {}
  	for repo in raw:
  		for link in repo['links']['clone']:
  			if link['name'] == 'ssh':
  				repos[repo['slug']] = link['href']
  	return repos
