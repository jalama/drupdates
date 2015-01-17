from drupdates.utils import *
from drupdates.repos import *

'''
Note: you need an ssh key set up with Stash to make this script work
'''

class repolist(repoTool):

  def __init__(self):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  def gitRepos(self):
    #Get list of Stash repos in the Rain Project.
    repoDict = self.settings.get('repoDict')
    if (not repoDict) or (type(repoDict) is not dict):
      return {}
    else:
      return repoDict

