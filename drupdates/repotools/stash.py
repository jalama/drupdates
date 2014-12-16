'''
Note: you need an ssh key set up with Stash to make this script work
'''

def gitRepos():
  #Get list of Stash repos in the Rain Project.
  r = apiCall(gitRepoURL, gitRepoName, 'get', auth=(uname, pword))
  repos = r['values']
  return repos