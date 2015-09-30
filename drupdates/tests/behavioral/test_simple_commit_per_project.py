""" Test running Drupdates on one repo, committing once per project. """

from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestSimpleCommitPerProject(object):
    """ Test running Drupdates on one repo. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir
        self.utils = BehavioralUtils()

    @staticmethod
    def test_repo_built():
        """ Test to ensure one repo built successfully. """

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
    def test_repo_commit_count():
        """ Test that the repo has 4 commits. """

        commit_count = BehavioralUtils.count_commits('drupal', 'builds')
        assert commit_count == 4
