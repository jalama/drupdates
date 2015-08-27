""" Test Multiple repos, multiple working directories. """

import os
from drupdates.tests.behavioral.behavioral_utils import BehavioralUtils
from drupdates.tests import Setup

class TestMultipleWorkingDirectoriesMultipleSites(object):
    """ Test Multiple repos, multiple working directories. """

    @classmethod
    def setup_class(cls):
        """ Setup test class. """
        utils = BehavioralUtils()
        utils.build(__file__)

    def __init__(self):
        base = Setup()
        self.test_directory = base.test_dir

    def test_repo_built(self):
        """ Test to ensure both repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds')
        # If 2 repos Siteupdates in report repo built successfully.
        assert count == 1

    def test_second_repo_built(self):
        """ Test to ensure both repos built successfully. """

        count = BehavioralUtils.count_repos_updated('builds/test')
        # If 2 repos Siteupdates in report repo built successfully.
        assert count == 1

    def test_frst_repo_updated(self):
        """ Test to ensure the repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'drupal', 'builds')
        assert report_status == status

    def test_second_repo_updated(self):
        """ Test to ensure the second repo was updated. """

        status = "The following updates were applied"
        report_status = BehavioralUtils.check_repo_updated(self.test_directory, 'drupal_test', 'builds/test')
        assert report_status == status
