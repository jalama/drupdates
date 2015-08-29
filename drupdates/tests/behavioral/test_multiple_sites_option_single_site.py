""" Test multiple sites, passing singleSite option on CLI. """

"""
    note: Only the one site, labeled 'drupal' should be updated.
"""
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleSiteOptionSingleSite(object):
    """ Test multiple sites, passing singleSite option on CLI. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    @staticmethod
    def test_one_repo_built():
        """ Test to ensure one of three repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 1 repo Siteupdates in report repo built successfully.
        assert count == 1

    @staticmethod
    def test_first_repo_updated():
        """ Test to ensure the first repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated('drupal', 'builds')
        assert report_status == status
