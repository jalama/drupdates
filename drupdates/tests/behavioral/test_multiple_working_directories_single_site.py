""" Test Multiple repos, multiple working directories, passing singleSite. """

"""
    note: Both sites should get updated as singleSite won't work with multiple
    working directories.
"""
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleWorkingDirectoriesSingleSites(object):
    """ Test multiple repos, multiple working directories, pass singleSite. """

    @classmethod
    def setup_class(cls):
        """ Setup test class."""
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_repo_built():
        """ Test to ensure both repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 1 repo Siteupdates in report repo built successfully in builds dir.
        assert count == 1

    @staticmethod
    def test_second_repo_built():
        """ Test to ensure both repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds/test')
        # If 1 repo Siteupdates in report repo built successfully in builds/test.
        assert count == 1

    @staticmethod
    def test_frst_repo_updated():
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds')
        assert report_status == status

    @staticmethod
    def test_second_repo_updated():
        """ Test to ensure the second repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal_test', 'builds/test')
        assert report_status == status
