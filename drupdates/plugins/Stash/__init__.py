""" Plugin to pull a git repo list from the Stash. """
from drupdates.settings import Settings
from drupdates.utils import utils
from drupdates.constructors.repos import Repotool
import os

'''
Note: you need an ssh key set up with Stash to make this script work
'''

class Stash(Repotool):
    """ Return git repository list from Stash project. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.settings = Settings(current_dir)

    def git_repos(self):
        """Get list of Stash repos from a specific Project."""
        stash_url = self.settings.get('stashURL')
        git_repo_name = self.settings.get('gitRepoName')
        stash_user = self.settings.get('stashUser')
        stash_pword = self.settings.get('stashPword')
        stash_cert_verify = self.settings.get('stashCertVerify')
        response = utils.apiCall(stash_url, git_repo_name, 'get',
                                 auth=(stash_user, stash_pword), verify=stash_cert_verify)
        if not response == False:
            repos = Stash.parse_repos(response['values'])
            return repos
        else:
            return {}

    @staticmethod
    def parse_repos(raw):
        """ Parse repo list returned form Stash."""
        repos = {}
        for repo in raw:
            for link in repo['links']['clone']:
                if link['name'] == 'ssh':
                    repos[repo['slug']] = link['href']
        return repos
