from drupdates.utils import *
from drupdates.constructors.repos import *

class repolist(repoTool):

  def __init__(self):
    self.currentDir = os.path.dirname(os.path.realpath(__file__))
    self.settings = Settings(self.currentDir)

  def gitRepos(self):
    """Return a  list of repos from the Settings.

    The expected format is a dictionary whose keys are the folder names and
    values are the ssh connection strings to the repo.

    Example:
    {
    'drupal': 'http://git.drupal.org/project/drupal.git'
    }

    """
    repoDict = self.settings.get('repoDict')
    if (not repoDict) or (type(repoDict) is not dict):
      return {}
    else:
      return repoDict

