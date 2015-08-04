""" Plugin to pull a git repo list from the Stash. """
from drupdates.settings import Settings
from drupdates.utils import Utils
from drupdates.constructors.repos import Repotool
import os

'''
Note: you need an ssh key set up with Stash to make this script work
'''

class Stash(Repotool):
    """ Return git repository list from Stash project. """

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file = current_dir + '/settings/default.yaml'
        self.settings = Settings()
        self.settings.add(settings_file)

    def git_repos(self):
        """ Get list of Stash repos from a specific Project.

            Note: this request will only bring back 9,999 repos, which should
            suffice, if it doesn't updaqte the stashLimit setting.
        """
        stash_url = self.settings.get('stashURL')
        git_repo_name = self.settings.get('gitRepoName')
        stash_user = self.settings.get('stashUser')
        stash_pword = self.settings.get('stashPword')
        stash_cert_verify = self.settings.get('stashCertVerify')
        stash_limit = self.settings.get('stashLimit')
        stash_params = {'limit' : stash_limit}
        response = Utils.api_call(stash_url, git_repo_name, 'get',
                                  auth=(stash_user, stash_pword),
                                  verify=stash_cert_verify,
                                  params=stash_params)
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
