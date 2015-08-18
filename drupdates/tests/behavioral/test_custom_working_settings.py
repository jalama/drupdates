""" Test running Drupdates on one repo. """
import os, yaml
from git import Repo
from os.path import expanduser
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestCustomWorkingSettings(object):
    """ Test on one repo with custom settings file. """

    @classmethod
    def setup_class(cls):
        """ Setup the test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure one repos built successfully. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        # If 1 repo Siteupdates in report repo built successfully.
        assert len(updates) == 1

    def test_repo_updated(self):
        """ Test to ensure the repo was updated. """

        file_name = open(os.path.join(self.test_directory, 'results.txt'), 'r')
        results = file_name.readlines()
        updates = BehavioralUtils.list_duplicates_of(results, 'Siteupdate \n')
        index = updates[0]
        status = "status : The following updates were applied"
        assert results[index + 1].strip() == status

    @staticmethod
    def test_git_commit_author():
        """ Test to verify the name of the git commit is "Drupdates". """

        file_name = open(os.path.join(expanduser('~'), '.drupdates', 'settings.yaml'), 'r')
        settings = yaml.load(file_name)
        working_dir = os.path.join(expanduser('~'), '.drupdates', 'builds')
        folder = os.path.join(working_dir, settings['repoDict']['value']['drupal'])
        repo = Repo(folder)
        devcommit = repo.heads.dev.commit
        assert devcommit.author.name == 'Drupdates'
