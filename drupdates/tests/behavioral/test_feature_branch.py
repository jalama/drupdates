""" Test running Drupdates and commit to feature branch in origin repo. """
import os, yaml
from git import Repo
from os.path import expanduser
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestFeatureBranch(object):
    """ Test committing to feature branch in lieu of working branch. """

    @classmethod
    def setup_class(cls):
        """ Setup the test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_repo_built():
        """ Test to ensure one repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 1 repo Siteupdates in report repo built successfully.
        assert count == 1

    @staticmethod
    def test_repo_updated():
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds')
        assert report_status == status

    @staticmethod
    def test_git_drupdates_branch():
        """ Test to verify the name of the git commit is 'Security Updates'. """

        commit = BehavioralUtils.get_drupdates_commit('drupal', 'builds')
        assert commit.author.name == 'Security Updates'
