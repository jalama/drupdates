""" Plugin to pull a repo list from the settings file. """
from drupdates.settings import Settings
from drupdates.constructors.repos import Repotool
import os

class Repolist(Repotool):
    """ Return git repository list manually maintained in the settings file. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)

    def git_repos(self):
        """Return a  list of repos from the Settings.

        The expected format is a dictionary whose keys are the folder names and
        values are the ssh connection strings to the repo.

        Example:
        {
        'drupal': 'http://git.drupal.org/project/drupal.git'
        }

        """
        repo_dict = self.settings.get('repoDict')
        if (not repo_dict) or (not isinstance(repo_dict, dict)):
            return {}
        else:
            return repo_dict

