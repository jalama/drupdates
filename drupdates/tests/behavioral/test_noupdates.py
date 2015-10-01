""" Test running Drupdates on one repo not needing updates. """

from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestNoupdates(object):
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
        """ Test to ensure the repo didn't need updated. """

        status = "Did not have any updates to apply"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds')
        assert report_status == status

    @staticmethod
    def test_files_modified():
        """ Test to make sure no cached/indexed files were modified. """

        modified_count = BehavioralUtils.count_modified_files('drupal', 'builds')
        assert modified_count == 0
